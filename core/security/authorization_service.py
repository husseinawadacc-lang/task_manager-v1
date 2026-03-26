"""
Authorization Service

Central place for checking RBAC permissions.

Responsibilities:
- Check if a role has permission
- Check if a user can perform an action
- Provide a consistent interface for authorization

This prevents permission logic from being scattered
across services and APIs.
"""

from core.enums.permission import Permission
from core.enums.role import UserRole
from core.security.permissions_map import ROLE_PERMISSIONS
from utils.logger import get_logger
from domain.user import User
from utils.exceptions import ForbiddenError
logger = get_logger(__name__)

class AuthorizationService:

    @staticmethod
    def role_has_permission(role: UserRole, permission: Permission) -> bool:
        """
        Check if a role has a specific permission.
        """

        role_permissions = ROLE_PERMISSIONS.get(role, set())

        return permission in role_permissions


    @staticmethod
    def check_permission(user:User, permission: Permission) -> bool:
        """
        Check if user has permission.
        """

        return AuthorizationService.role_has_permission(
            user.role,
            permission
        )


    @staticmethod
    def require_permission(user:User, permission: Permission):
        """
        Enforce permission.

        Raises:
            PermissionError if not allowed
        """

        if not AuthorizationService.check_permission(user, permission):
            
            logger.warning(
                        "Permission denied",
                        extra={
                            "user_id": user.id,
                            "role":user.role,
                            "permission": permission }  )
            raise ForbiddenError("permission denied")