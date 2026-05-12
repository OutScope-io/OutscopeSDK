from __future__ import annotations
from typing import List, Dict, Any, Optional
from ..http import HttpClient


class AssetsResource:
    """Manage asset inventory."""

    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    def create(
        self,
        target: str,
        company_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new asset manually.
        
        Args:
            target: Target (domain, IP, or URL)
            company_id: Company ID (uses 'Default' if not provided)
            name: Human-readable asset name
            description: Asset description
            tags: Tags for categorization
            metadata: Custom metadata
            
        Returns:
            Created asset data
        """
        data = {"target": target}
        
        if company_id is not None:
            data["company_id"] = company_id
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if tags is not None:
            data["tags"] = tags
        if metadata is not None:
            data["metadata"] = metadata
        
        return self._http_client.request("POST", "/assets/", data=data)

    def list(
        self,
        page: int = 1,
        per_page: int = 50,
        search: Optional[str] = None,
        tags: Optional[str] = None,
        active_only: bool = True,
        analyzability: Optional[str] = None,
        reasons: Optional[str] = None,
        category: Optional[str] = None,
        company_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """List assets with filtering and pagination.
        
        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 50, max: 100)
            search: Search in target, name, description
            tags: Comma-separated tags to filter by
            active_only: Only return active assets (default: True)
            analyzability: Filter by analyzability (all, analyzable, not_analyzable)
            reasons: Comma-separated reasons to filter by
            category: Category filter
            company_id: Filter by company ID
            
        Returns:
            Dict with assets, total, page, per_page
        """
        params = {"page": page, "per_page": per_page, "active_only": str(active_only).lower()}
        
        if search:
            params["search"] = search
        if tags:
            params["tags"] = tags
        if analyzability:
            params["analyzability"] = analyzability
        if reasons:
            params["reasons"] = reasons
        if category:
            params["category"] = category
        if company_id:
            params["company_id"] = company_id
        
        return self._http_client.request("GET", "/assets/", params=params)

    def get(self, asset_id: str) -> Dict[str, Any]:
        """Get single asset by ID.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Asset data
        """
        return self._http_client.request("GET", f"/assets/{asset_id}")

    def update(
        self,
        asset_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        active: Optional[bool] = None,
        schedule: Optional[str] = None,
        company_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update asset information.
        
        Args:
            asset_id: Asset ID
            name: New asset name
            description: New description
            tags: New tags list
            metadata: New metadata
            active: Active status
            schedule: Check schedule (none, hourly, daily, weekly)
            company_id: Company ID to assign asset to
            
        Returns:
            Updated asset data
        """
        data = {}
        
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if tags is not None:
            data["tags"] = tags
        if metadata is not None:
            data["metadata"] = metadata
        if active is not None:
            data["active"] = active
        if schedule is not None:
            data["schedule"] = schedule
        if company_id is not None:
            data["company_id"] = company_id
        
        return self._http_client.request("PUT", f"/assets/{asset_id}", data=data)

    def delete(self, asset_id: str) -> None:
        """Delete asset (soft delete - marks as inactive).
        
        Args:
            asset_id: Asset ID
        """
        self._http_client.request("DELETE", f"/assets/{asset_id}")

    def set_schedule(self, asset_id: str, schedule: str) -> Dict[str, Any]:
        """Set the recurring check schedule for an asset.
        
        Args:
            asset_id: Asset ID
            schedule: Check schedule (none, hourly, daily, weekly)
            
        Returns:
            Dict with message, asset_id, target, schedule
        """
        data = {"schedule": schedule}
        return self._http_client.request("PUT", f"/assets/{asset_id}/schedule", data=data)

    def trigger_check(self, asset_id: str) -> Dict[str, Any]:
        """Trigger a manual check for this specific asset.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Dict with message, job_id, asset_id, target, status, queue
        """
        return self._http_client.request("POST", f"/assets/{asset_id}/check")

    def get_stats(self) -> Dict[str, Any]:
        """Get asset statistics overview.
        
        Returns:
            Dict with total_assets, manual_assets, auto_discovered, recent_checks, top_tags
        """
        return self._http_client.request("GET", "/assets/stats/overview")

    def get_checks(
        self,
        asset_id: str,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get check history for a specific asset.
        
        Args:
            asset_id: Asset ID
            page: Page number
            limit: Items per page (max: 100)
            
        Returns:
            Dict with asset_id, target, checks, total, page, limit
        """
        params = {"page": page, "limit": limit}
        return self._http_client.request("GET", f"/assets/{asset_id}/checks", params=params)
