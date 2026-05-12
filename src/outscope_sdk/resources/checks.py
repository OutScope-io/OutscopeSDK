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

    def list(
        self, 
        page: int = 1, 
        limit: int = 50, 
        fqdn: Optional[str] = None,
        analyzability: Optional[str] = None,
        reasons: Optional[str] = None,
        category: Optional[str] = None,
        company_id: Optional[str] = None
    ) -> Any:
        """List checks with pagination and filters.
        
        Args:
            page: Page number (default: 1)
            limit: Items per page (default: 50, max: 100)
            fqdn: Filter by FQDN (partial match)
            analyzability: Filter by analyzability status ("all", "analyzable", "not_analyzable")
            reasons: Comma-separated list of reasons to filter by
            category: Filter by category
            company_id: Filter by company ID
        """
        params = {"page": page, "limit": min(limit, 100)}
        if fqdn:
            params["fqdn"] = fqdn
        if analyzability:
            params["analyzability"] = analyzability
        if reasons:
            params["reasons"] = reasons
        if category:
            params["category"] = category
        if company_id:
            params["company_id"] = company_id
        return self._http_client.request("GET", "/checks", params=params)
    
    def list_all(
        self, 
        limit: int = 50, 
        fqdn: Optional[str] = None,
        analyzability: Optional[str] = None,
        reasons: Optional[str] = None,
        category: Optional[str] = None,
        company_id: Optional[str] = None
    ) -> Iterator[Dict[str, Any]]:
        """Iterate through all checks automatically with filters."""
        page = 1
        while True:
            response = self.list(
                page=page, 
                limit=limit, 
                fqdn=fqdn,
                analyzability=analyzability,
                reasons=reasons,
                category=category,
                company_id=company_id
            )
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
        ports: Optional[list] = None, 
        max_redirects: Optional[int] = None,
        collect_content_sample: Optional[bool] = None,
        content_sample_retention_days: Optional[int] = None,
        pool_id: Optional[str] = None,
        company_id: Optional[str] = None
    ) -> Any:
        """Create a new security check.
        
        Args:
            fqdn: Fully qualified domain name to check
            paths: List of paths to check (default: ["/"])
            ports: List of ports to check (default: [80, 443])
            max_redirects: Maximum number of redirects to follow (0 or 1, default: 0)
            collect_content_sample: Whether to collect HTTP response content sample
            content_sample_retention_days: Days to retain content sample (1-90)
            pool_id: Worker pool to use for this check (optional)
            company_id: Company ID to associate with this check (optional)
        """
        check_data = {
            "fqdn": fqdn,
        }
        
        if paths is not None:
            check_data["paths"] = paths
        if ports is not None:
            check_data["ports"] = ports
        if max_redirects is not None:
            check_data["max_redirects"] = max_redirects
        if collect_content_sample is not None:
            check_data["collect_content_sample"] = collect_content_sample
        if content_sample_retention_days is not None:
            check_data["content_sample_retention_days"] = content_sample_retention_days
        if pool_id is not None:
            check_data["pool_id"] = pool_id
        if company_id is not None:
            check_data["company_id"] = company_id

        data = self._http_client.request("POST", "/check", data=check_data)
        return Check.from_api(data)
    
    def create_batch(
        self,
        domains: List[str],
        paths: Optional[List[str]] = None,
        ports: Optional[List[int]] = None,
        max_redirects: Optional[int] = None,
        collect_content_sample: Optional[bool] = None,
        content_sample_retention_days: Optional[int] = None,
        pool_id: Optional[str] = None,
        company_id: Optional[str] = None,
        check_usage_first: bool = True,
        wait_on_limits: bool = True,
        max_retries: int = 5,
        progress_callback: Optional[Callable[[int, int, Dict], None]] = None
    ) -> Dict[str, Any]:
        """Create multiple checks with automatic rate limit handling.
        
        Args:
            domains: List of domains to check
            paths: List of paths to check (default: ["/"])
            ports: List of ports to check (default: [443])
            max_redirects: Maximum number of redirects to follow (0 or 1, default: 0)
            collect_content_sample: Whether to collect HTTP response content sample
            content_sample_retention_days: Days to retain content sample (1-90)
            pool_id: Worker pool to use for checks (optional)
            company_id: Company ID to associate with checks (optional)
            check_usage_first: Check if quota is sufficient before starting
            wait_on_limits: Wait and retry when rate limited
            max_retries: Maximum number of retries per domain
            progress_callback: Callback function for progress updates
        """
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
                max_redirects=max_redirects,
                collect_content_sample=collect_content_sample,
                content_sample_retention_days=content_sample_retention_days,
                pool_id=pool_id,
                company_id=company_id,
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
        max_redirects: Optional[int],
        collect_content_sample: Optional[bool],
        content_sample_retention_days: Optional[int],
        pool_id: Optional[str],
        company_id: Optional[str],
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
                    max_redirects=max_redirects,
                    collect_content_sample=collect_content_sample,
                    content_sample_retention_days=content_sample_retention_days,
                    pool_id=pool_id,
                    company_id=company_id
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

    def latest(self, fqdn: str) -> Any:
        """Get the latest completed check for a given FQDN.
        
        Args:
            fqdn: Fully qualified domain name
            
        Returns:
            Latest completed check data
        """
        params = {"fqdn": fqdn}
        return self._http_client.request("GET", "/check/latest", params=params)

    def cancel(self, check_id: str) -> Any:
        """Cancel a queued or running check.
        
        Args:
            check_id: Check ID to cancel
            
        Returns:
            Cancellation confirmation data
        """
        return self._http_client.request("DELETE", f"/check/{check_id}")

    def send_review(self, check_id: str, reason: str, comments: str) -> None:
        """Send a review request for a check.
        
        Args:
            check_id: Check ID to review
            reason: Reason for the review request
            comments: Additional comments
        """
        data = {
            "job_id": check_id,
            "reason": reason,
            "comments": comments
        }
        self._http_client.request("POST", "/check/review", data=data)

    def get_review_status(self, check_id: str) -> Any:
        """Get review status for a check.
        
        Args:
            check_id: Check ID
            
        Returns:
            Review status information
        """
        return self._http_client.request("GET", f"/check/{check_id}/review-status")

    def get_queue_status(self, check_id: str) -> Any:
        """Get queue status for a check (MongoDB + Celery).
        
        Args:
            check_id: Check ID
            
        Returns:
            Queue status information
        """
        return self._http_client.request("GET", f"/check/{check_id}/queue-status")

