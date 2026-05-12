from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class WorkerPool:
    queue_name: str
    display_name: str
    type: str  # "tenant" | "plan" | "shared"
    available: bool
    agent_id: Optional[str]

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> WorkerPool:
        return cls(
            queue_name=data["queue_name"],
            display_name=data["display_name"],
            type=data["type"],
            available=data["available"],
            agent_id=data.get("agent_id")
        )
