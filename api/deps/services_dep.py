# ==========================================================
# Services Dependency Injection
# ==========================================================
"""
This module wires all services using FastAPI Depends.

Design Principles:
------------------
✔ Each request gets fresh service instances
✔ Dependencies are injected (NOT created manually in endpoints)
✔ Storage is abstracted (SQLAlchemy / Memory interchangeable)
✔ UnitOfWork manages transactions (NOT API layer)

Flow:
API → Depends → Service → Storage → DB
"""

from fastapi import Depends

# ==========================================================
# STORAGE
# ==========================================================

from storage.base_st import BaseStorage
from storage.st_factory import get_storage

# ==========================================================
# CORE SERVICES
# ==========================================================

from services.unit_of_work import UnitOfWork
from services.password_policy_service import PasswordPolicyService
from services.audit_service import AuditService
# ==========================================================
# BUSINESS SERVICES
# ==========================================================

from services.task_service import TaskService
from services.project_service import ProjectService
from services.token_services import TokenService
from services.auth_service import AuthService
from services.password_reset_services import PasswordResetService
from services.project_service import ProjectService

# ==========================================================
# UnitOfWork
# ==========================================================

def get_unit_of_work() -> UnitOfWork:
    """
    Provide UnitOfWork instance.

    Responsibilities:
    - Open DB session
    - Handle commit/rollback
    - Ensure transaction integrity
    """
    return UnitOfWork()


# ==========================================================
# Password Policy
# ==========================================================

def get_password_policy_service() -> PasswordPolicyService:
    """
    Stateless service.

    Safe to instantiate per request.
    No DB access required.
    """
    return PasswordPolicyService()

# ========================================================
# audit service
# ========================================================

def get_audit_service(
    storage = Depends(get_storage),

) -> AuditService:
    return AuditService(
        storage=storage,
            )


# ==========================================================
# ProjectService 🔥 NEW
# ==========================================================

def get_project_service(
    storage: BaseStorage = Depends(get_storage),
    uow: UnitOfWork = Depends(get_unit_of_work),
    audit_service:AuditService = Depends(get_audit_service)
) -> ProjectService:
    """
    ProjectService dependency.

    Handles:
    - Project creation
    - Ownership isolation
    - SaaS structure
    """

    return ProjectService(
        storage=storage,
        uow=uow,
        audit_service=audit_service,
    )

# ==========================================================
# TaskService
# ==========================================================

def get_task_service(
    storage: BaseStorage = Depends(get_storage),
    uow: UnitOfWork = Depends(get_unit_of_work),
    project_service:ProjectService= Depends(get_project_service),
    audit_service:AuditService = Depends(get_audit_service)
) -> TaskService:
    """
    TaskService dependency.

    Handles:
    - Task CRUD
    - Business rules
    - Security (ownership)
    - AI priority
    """

    return TaskService(
        storage=storage,
        uow=uow,
        project_service=project_service,
        audit_service=audit_service,
    )


# ==========================================================
# TokenService
# ==========================================================

def get_token_service(
    storage: BaseStorage = Depends(get_storage),
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> TokenService:
    """
    TokenService dependency.

    Handles:
    - JWT creation
    - Refresh tokens
    - Token lifecycle
    """

    return TokenService(
        storage=storage,
        uow=uow,
    )


# ==========================================================
# AuthService
# ==========================================================

def get_auth_service(
    storage: BaseStorage = Depends(get_storage),
    policy: PasswordPolicyService = Depends(get_password_policy_service),
    uow: UnitOfWork = Depends(get_unit_of_work),
    token_service: TokenService = Depends(get_token_service),
) -> AuthService:
    """
    AuthService dependency.

    Handles:
    - Login / Register
    - Password validation
    - Token issuing
    """

    return AuthService(
        storage=storage,
        password_policy=policy,
        uow=uow,
        token_service=token_service,
    )


# ==========================================================
# Password Reset Service
# ==========================================================

def get_password_reset_service(
    storage: BaseStorage = Depends(get_storage),
    policy: PasswordPolicyService = Depends(get_password_policy_service),
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> PasswordResetService:
    """
    Password reset flow.

    Handles:
    - Generate reset token
    - Validate token
    - Update password securely
    """

    return PasswordResetService(
        storage=storage,
        password_policy=policy,
        uow=uow,
    )