from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ClientConfig:
    """Client configuration."""
    api_key: str
    base_url: str = "https://api.outscope.es/v1"
    timeout: float = 30.0
    user_agent: str = "OutScopeSDK/0.1.0"
