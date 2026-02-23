from __future__ import annotations
from typing import Optional
from .config import ClientConfig
from .http import HttpClient
from .resources.checks import ChecksResource
from .resources.usage import UsageResource


class Client:
    """OutScope API client for managing security checks."""

    def __init__(self, api_key: str, base_url: Optional[str] = None, timeout: float = 30.0) -> None:
        config = ClientConfig(
            api_key=api_key,
            base_url=base_url or ClientConfig.base_url,
            timeout=timeout,
        )
        self._http_client = HttpClient(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
            user_agent=config.user_agent,
        )

        self.checks = ChecksResource(self._http_client)
        self.usage = UsageResource(self._http_client)

    def close(self) -> None:
        """Close HTTP client and cleanup resources."""
        self._http_client.client.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

