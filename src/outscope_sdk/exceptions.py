from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Dict


@dataclass
class ApiError(Exception):
    """Base exception for API errors."""
    message: str
    status_code: Optional[int] = None
    details: Optional[Any] = None

    def __str__(self) -> str:
        base_message = f"ApiError: {self.message}"
        if self.status_code is not None:
            base_message += f" (Status Code: {self.status_code})"
        if self.details is not None:
            base_message += f" | Details: {self.details}"
        return base_message


class AuthenticationError(ApiError):
    """Authentication failed."""
    pass


class RateLimitError(ApiError):
    """Rate limit exceeded."""
    
    def __init__(self, message: str, status_code: int = 429, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code, details)
        self.code = details.get("code") if details else None
        self.retry_after = details.get("retry_after") if details else None
        self.limit = details.get("limit") if details else None
        self.remaining = details.get("remaining") if details else None
        self.reset_at = details.get("reset_at") if details else None
        self.current = details.get("current") if details else None
        self.used = details.get("used") if details else None
        self.period = details.get("period") if details else None
    
    def __str__(self) -> str:
        base_message = f"RateLimitError: {self.message}"
        if self.code:
            base_message += f" (Code: {self.code})"
        if self.retry_after is not None:
            base_message += f" | Retry after: {self.retry_after}s"
        if self.limit:
            base_message += f" | Limit: {self.limit}"
        return base_message


class NotFoundError(ApiError):
    """Resource not found."""
    pass


class ValidationError(ApiError):
    """Request validation failed."""
    pass


class ServerError(ApiError):
    """Server error."""
    pass

