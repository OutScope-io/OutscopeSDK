from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Company:
    id: str
    name: str
    active: bool
    tenant_id: str

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> Company:
        return cls(
            id=data["id"],
            name=data["name"],
            active=data["active"],
            tenant_id=data["tenant_id"]
        )
