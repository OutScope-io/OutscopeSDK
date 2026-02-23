from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Check:
    job_id: str
    status: str
    raw: Dict[str, Any]

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> Check:
        return cls(
            job_id=data["job_id"],
            status=data["status"],
            raw=data
        )
