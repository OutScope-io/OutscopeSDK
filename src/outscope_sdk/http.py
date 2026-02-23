from __future__ import annotations
from typing import Any, Dict, Optional
import httpx

from .exceptions import (
    ApiError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError
)


class HttpClient:
    """HTTP client for API requests."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.outscope.es/v1",
        timeout: int = 30,
        user_agent: str = "OutScopeSDK/0.1.0",
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.user_agent = user_agent
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "x-api-key": self.api_key,
                "User-Agent": self.user_agent,
                "Content-Type": "application/json",
            },
        )

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make HTTP request and handle errors."""
        response = self.client.request(
            method=method,
            url=endpoint,
            params=params,
            json=data,
        )

        if response.status_code >= 200 and response.status_code < 300:
            return response.json()

        if response.status_code == 401:
            raise AuthenticationError("Authentication failed.", status_code=401)
        elif response.status_code == 404:
            raise NotFoundError("Resource not found.", status_code=404)
        elif response.status_code == 429:
            try:
                error_details = response.json()
                message = error_details.get("message", "Rate limit exceeded.")
                raise RateLimitError(message, status_code=429, details=error_details)
            except Exception:
                raise RateLimitError("Rate limit exceeded.", status_code=429)
        elif response.status_code == 400:
            raise ValidationError("Validation error.", status_code=422, details=response.json())
        elif 500 <= response.status_code < 600:
            raise ServerError("Server error occurred.", status_code=response.status_code)

        raise ApiError(
            "An unexpected error occurred.",
            status_code=response.status_code,
            details=response.text,
        )

    def close(self) -> None:
        """Close HTTP client."""
        self.client.close()

