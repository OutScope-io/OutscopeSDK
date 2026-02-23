from __future__ import annotations
from typing import Any, Dict, Optional, Iterator, List, Callable
import time
from ..http import HttpClient
from ..models.check import Check
from ..exceptions import RateLimitError


class ChecksResource:
    """Manage security checks."""

    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    def list(self, page: int = 1, limit: int = 50, fqdn: Optional[str] = None) -> Any:
        """List checks with pagination."""
        params = {"page": page, "limit": min(limit, 100)}
        if fqdn:
            params["fqdn"] = fqdn
        return self._http_client.request("GET", "/checks", params=params)
    
    def list_all(self, limit: int = 50, fqdn: Optional[str] = None) -> Iterator[Dict[str, Any]]:
        """Iterate through all checks automatically."""
        page = 1
        while True:
            response = self.list(page=page, limit=limit, fqdn=fqdn)
            items = response.get("items", [])
            
            if not items:
                break
                
            for item in items:
                yield item
            
            if len(items) < limit:
                break
                
            page += 1

    def get(self, check_id: str) -> Any:
        """Get check details by ID."""
        return self._http_client.request("GET", f"/check/{check_id}")

    def create(
        self, 
        fqdn: str, 
        paths: Optional[list] = None, 
        ports: Optional[int] = None, 
        redirects: Optional[bool] = None,
        include_content_sample: Optional[bool] = None,
        content_sample_retention_days: Optional[int] = None
    ) -> Any:
        """Create a new security check."""
        check_data = {
            "fqdn": fqdn,
        }
        
        if paths is not None:
            check_data["paths"] = paths
        if ports is not None:
            check_data["ports"] = ports
        if redirects is not None:
            check_data["redirects"] = 1 if redirects else 0
        if include_content_sample is not None:
            check_data["include_content_sample"] = include_content_sample
        if content_sample_retention_days is not None:
            check_data["content_sample_retention_days"] = content_sample_retention_days

        data = self._http_client.request("POST", "/check", data=check_data)
        return Check.from_api(data)
    
    def create_batch(
        self,
        domains: List[str],
        paths: Optional[List[str]] = None,
        ports: Optional[List[int]] = None,
        redirects: Optional[bool] = None,
        include_content_sample: Optional[bool] = None,
        content_sample_retention_days: Optional[int] = None,
        check_usage_first: bool = True,
        wait_on_limits: bool = True,
        max_retries: int = 5,
        progress_callback: Optional[Callable[[int, int, Dict], None]] = None
    ) -> Dict[str, Any]:
        """Create multiple checks with automatic rate limit handling."""
        from ..client import Client
        
        # Defaults
        if paths is None:
            paths = ["/"]
        if ports is None:
            ports = [443]
        
        stats = {
            'total': len(domains),
            'created': 0,
            'failed': 0,
            'rate_limited': 0,
            'inflight_limited': 0,
            'quota_exceeded': 0,
            'retries': 0
        }
        
        results = []
        start_time = time.time()
        
        # Check quota first
        if check_usage_first:
            usage = self._http_client.request("GET", "/usage")
            available = usage['usage']['checks_limit'] - usage['usage']['checks_used']
            
            if available < len(domains):
                raise ValueError(
                    f"Insufficient quota: need {len(domains)} checks but only {available} available. "
                    f"Consider reducing batch size or upgrading your plan."
                )
        
        # Process domains
        for i, domain in enumerate(domains, 1):
            result = self._create_with_retry(
                domain=domain,
                paths=paths,
                ports=ports,
                redirects=redirects,
                include_content_sample=include_content_sample,
                content_sample_retention_days=content_sample_retention_days,
                max_retries=max_retries,
                wait_on_limits=wait_on_limits,
                stats=stats
            )
            
            if result:
                results.append(result)
                stats['created'] += 1
            else:
                stats['failed'] += 1
            
            # Report progress
            if progress_callback and i % 10 == 0:
                progress_callback(i, len(domains), stats)
        
        duration = time.time() - start_time
        
        return {
            'results': results,
            'stats': stats,
            'duration': duration
        }
    
    def _create_with_retry(
        self,
        domain: str,
        paths: List[str],
        ports: List[int],
        redirects: Optional[bool],
        include_content_sample: Optional[bool],
        content_sample_retention_days: Optional[int],
        max_retries: int,
        wait_on_limits: bool,
        stats: Dict[str, int]
    ) -> Optional[Dict[str, Any]]:
        """Create check with retry."""
        
        for attempt in range(max_retries):
            try:
                check = self.create(
                    fqdn=domain,
                    paths=paths,
                    ports=ports,
                    redirects=redirects,
                    include_content_sample=include_content_sample,
                    content_sample_retention_days=content_sample_retention_days
                )
                
                if attempt > 0:
                    stats['retries'] += 1
                
                return {
                    'domain': domain,
                    'job_id': check.job_id,
                    'status': check.status,
                    'attempts': attempt + 1
                }
                
            except RateLimitError as e:
                if e.code == "rate_limit_exceeded":
                    stats['rate_limited'] += 1
                    if wait_on_limits and attempt < max_retries - 1:
                        time.sleep(e.retry_after or 60)
                    elif attempt == max_retries - 1:
                        return None
                
                elif e.code == "inflight_limit":
                    stats['inflight_limited'] += 1
                    if wait_on_limits and attempt < max_retries - 1:
                        time.sleep(e.retry_after or 10)
                    elif attempt == max_retries - 1:
                        return None
                
                elif e.code == "checks_limit":
                    stats['quota_exceeded'] += 1
                    return None
            
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(min(2 ** attempt, 60))
                else:
                    return None
        
        return None


