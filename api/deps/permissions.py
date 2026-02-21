from fastapi import Depends, HTTPException, status
from models.user import  User
from api.deps.auth import get_current_user
from core.enums.user_role import UserRole

def require_roles(*allowed_roles: UserRole):
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user
    return dependency