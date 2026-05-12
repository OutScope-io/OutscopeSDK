from __future__ import annotations
from typing import List, Dict, Any, Optional
from ..http import HttpClient


class ReportsResource:
    """Manage report templates and generated reports."""

    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    # ==================== TEMPLATES ====================

    def create_template(
        self,
        name: str,
        description: Optional[str] = None,
        branding: Optional[Dict[str, Any]] = None,
        sections: Optional[List[Dict[str, Any]]] = None,
        default_filters: Optional[Dict[str, Any]] = None,
        output_format: str = "pdf",
        is_default: bool = False,
        company_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new report template.
        
        Args:
            name: Template name
            description: Template description
            branding: Branding configuration (logo_url, company_name, colors, etc.)
            sections: List of report sections to include
            default_filters: Default filters for the report
            output_format: Output format (pdf, html)
            is_default: Set as default template
            company_id: Associate with company
            
        Returns:
            Created template data
        """
        data = {
            "name": name,
            "output_format": output_format,
            "is_default": is_default
        }
        
        if description is not None:
            data["description"] = description
        if branding is not None:
            data["branding"] = branding
        if sections is not None:
            data["sections"] = sections
        if default_filters is not None:
            data["default_filters"] = default_filters
        if company_id is not None:
            data["company_id"] = company_id
        
        return self._http_client.request("POST", "/reports/templates", data=data)

    def list_templates(
        self,
        company_id: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """List report templates.
        
        Args:
            company_id: Filter by company
            page: Page number
            per_page: Items per page
            
        Returns:
            Dict with templates, total, page, per_page
        """
        params = {"page": page, "per_page": per_page}
        if company_id:
            params["company_id"] = company_id
        
        return self._http_client.request("GET", "/reports/templates", params=params)

    def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get a specific report template.
        
        Args:
            template_id: Template ID
            
        Returns:
            Template data
        """
        return self._http_client.request("GET", f"/reports/templates/{template_id}")

    def update_template(
        self,
        template_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        branding: Optional[Dict[str, Any]] = None,
        sections: Optional[List[Dict[str, Any]]] = None,
        default_filters: Optional[Dict[str, Any]] = None,
        output_format: Optional[str] = None,
        is_default: Optional[bool] = None,
        company_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a report template.
        
        Args:
            template_id: Template ID
            name: New template name
            description: New description
            branding: Updated branding
            sections: Updated sections
            default_filters: Updated default filters
            output_format: New output format
            is_default: Set as default
            company_id: Associate with company
            
        Returns:
            Updated template data
        """
        data = {}
        
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if branding is not None:
            data["branding"] = branding
        if sections is not None:
            data["sections"] = sections
        if default_filters is not None:
            data["default_filters"] = default_filters
        if output_format is not None:
            data["output_format"] = output_format
        if is_default is not None:
            data["is_default"] = is_default
        if company_id is not None:
            data["company_id"] = company_id
        
        return self._http_client.request("PUT", f"/reports/templates/{template_id}", data=data)

    def delete_template(self, template_id: str) -> None:
        """Delete a report template.
        
        Args:
            template_id: Template ID
        """
        self._http_client.request("DELETE", f"/reports/templates/{template_id}")

    # ==================== LOGO MANAGEMENT ====================

    def upload_logo(self, file_path: str) -> Dict[str, Any]:
        """Upload a logo file for report branding.
        
        Args:
            file_path: Path to logo file (png, jpg, jpeg, svg)
            
        Returns:
            Dict with logo_url
        """
        import os
        from pathlib import Path
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        filename = os.path.basename(file_path)
        
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f)}
            # Note: This requires httpx to handle multipart/form-data
            response = self._http_client.client.post(
                f"{self._http_client.base_url}/v1/reports/upload-logo",
                files=files,
                headers={"Authorization": f"Bearer {self._http_client.api_key}"}
            )
            response.raise_for_status()
            return response.json()

    # ==================== REPORT GENERATION ====================

    def generate(
        self,
        template_id: str,
        title: str,
        description: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        company_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a new report (async).
        
        Args:
            template_id: Template to use
            title: Report title
            description: Report description
            filters: Report filters (overrides template defaults)
            company_id: Company ID for report
            
        Returns:
            Dict with report_id, status, message
        """
        data = {
            "template_id": template_id,
            "title": title
        }
        
        if description is not None:
            data["description"] = description
        if filters is not None:
            data["filters"] = filters
        if company_id is not None:
            data["company_id"] = company_id
        
        return self._http_client.request("POST", "/reports/generate", data=data)

    def list(
        self,
        company_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """List generated reports.
        
        Args:
            company_id: Filter by company
            status: Filter by status (generating, completed, failed)
            page: Page number
            per_page: Items per page
            
        Returns:
            Dict with reports, total, page, per_page
        """
        params = {"page": page, "per_page": per_page}
        if company_id:
            params["company_id"] = company_id
        if status:
            params["status"] = status
        
        return self._http_client.request("GET", "/reports", params=params)

    def get(self, report_id: str) -> Dict[str, Any]:
        """Get a specific report.
        
        Args:
            report_id: Report ID
            
        Returns:
            Report data
        """
        return self._http_client.request("GET", f"/reports/{report_id}")

    def download(self, report_id: str, output_path: str) -> None:
        """Download a generated report file.
        
        Args:
            report_id: Report ID
            output_path: Local path to save the report
        """
        # Get report file as bytes
        response = self._http_client.client.get(
            f"{self._http_client.base_url}/reports/{report_id}/download",
            headers={"Authorization": f"Bearer {self._http_client.api_key}"}
        )
        response.raise_for_status()
        
        # Save to file
        with open(output_path, 'wb') as f:
            f.write(response.content)

    def get_download_url(self, report_id: str) -> str:
        """Get download URL for a report.
        
        Args:
            report_id: Report ID
            
        Returns:
            Download URL
        """
        return f"{self._http_client.base_url}/reports/{report_id}/download"
