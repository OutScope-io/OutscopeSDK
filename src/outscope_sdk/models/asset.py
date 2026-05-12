from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class Asset:
    asset_id: str
    tenant_id: str
    target: str
    name: str
    active: bool
    discovery_method: str
    first_seen: str
    last_seen: str
    check_count: int
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    last_check: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    schedule: Optional[str] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> Asset:
        return cls(
            asset_id=data["asset_id"],
            tenant_id=data["tenant_id"],
            target=data["target"],
            name=data["name"],
            active=data["active"],
            discovery_method=data["discovery_method"],
            first_seen=data["first_seen"],
            last_seen=data["last_seen"],
            check_count=data["check_count"],
            company_id=data.get("company_id"),
            company_name=data.get("company_name"),
            description=data.get("description"),
            tags=data.get("tags"),
            metadata=data.get("metadata"),
            last_check=data.get("last_check"),
            analysis=data.get("analysis"),
            schedule=data.get("schedule")
        )
