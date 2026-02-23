from __future__ import annotations
from typing import Any
from ..http import HttpClient


class UsageResource:
    """Query usage and limits."""

    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    def get(self) -> Any:
        """Get usage and limits for current tenant."""
        return self._http_client.request("GET", "/usage")
