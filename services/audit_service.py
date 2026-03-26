from domain.audit_log import AuditLog
from datetime import datetime, timezone
from storage.base_st import BaseStorage


class AuditService:

    def __init__(self, storage:BaseStorage):
        self.storage = storage

    def log(
        self,
        *,
        session,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: int | None = None,
        details: dict | None = None,
    ):
        log = AuditLog(
            id=None,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            created_at=datetime.now(timezone.utc),
        )

        self.storage.create_audit_log(
            session=session,
            log=log,
        )