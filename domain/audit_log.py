from dataclasses import dataclass
from datetime import datetime


@dataclass
class AuditLog:
    id: int | None
    user_id: int
    action: str
    resource_type: str
    resource_id: int | None
    details: dict | None
    created_at: datetime