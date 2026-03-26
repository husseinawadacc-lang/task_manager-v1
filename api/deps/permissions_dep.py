from fastapi import Depends, HTTPException, status
from domain.user import User
from api.deps.auth_dep import get_current_user
from core.enums.permission import Permission
from core.security.authorization_service import AuthorizationService


def require_permission(permission: Permission):

    def permission_checker(current_user:User=Depends(get_current_user)):

        if not AuthorizationService.check_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        return current_user

    return permission_checker