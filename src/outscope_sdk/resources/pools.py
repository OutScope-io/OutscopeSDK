from __future__ import annotations
from typing import List, Dict, Any
from ..http import HttpClient
from ..models.pool import WorkerPool


class PoolsResource:
    """Manage worker pools."""

    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    def list(self) -> Dict[str, Any]:
        """Get available worker pools for the tenant.
        
        Returns:
            Dict with 'pools' (list of WorkerPool objects) and 'default' (default pool name)
        """
        data = self._http_client.request("GET", "/pools")
        
        # Convert pools to WorkerPool objects
        pools = [WorkerPool.from_api(p) for p in data.get("pools", [])]
        
        return {
            "pools": pools,
            "default": data.get("default", "general")
        }
