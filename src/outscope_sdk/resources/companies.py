from __future__ import annotations
from typing import List, Dict, Any
from ..http import HttpClient
from ..models.company import Company


class CompaniesResource:
    """Manage companies."""

    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    def list(self, active_only: bool = True) -> List[Company]:
        """List companies for the current tenant.
        
        Args:
            active_only: Only return active companies (default: True)
            
        Returns:
            List of Company objects
        """
        params = {}
        if active_only is not None:
            params["active_only"] = str(active_only).lower()
        
        data = self._http_client.request("GET", "/companies", params=params)
        return [Company.from_api(c) for c in data.get("companies", [])]

    def get(self, company_id: str) -> Company:
        """Get a specific company by ID.
        
        Args:
            company_id: Company ID
            
        Returns:
            Company object
        """
        data = self._http_client.request("GET", f"/companies/{company_id}")
        return Company.from_api(data.get("company", data))

    def create(self, name: str) -> Company:
        """Create a new company.
        
        Args:
            name: Company name
            
        Returns:
            Created Company object
        """
        data = self._http_client.request("POST", "/companies", data={"name": name})
        return Company.from_api(data.get("company", data))

    def update(self, company_id: str, name: str = None, active: bool = None) -> Company:
        """Update a company.
        
        Args:
            company_id: Company ID
            name: New company name (optional)
            active: Active status (optional)
            
        Returns:
            Updated Company object
        """
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if active is not None:
            update_data["active"] = active
            
        data = self._http_client.request("PUT", f"/companies/{company_id}", data=update_data)
        return Company.from_api(data.get("company", data))

    def delete(self, company_id: str) -> None:
        """Delete (deactivate) a company.
        
        Args:
            company_id: Company ID
        """
        self._http_client.request("DELETE", f"/companies/{company_id}")
