from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from services.auth_s import AuthService
from api.deps.services import get_auth_service
from utils.exceptions import TokenError
from models.user import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    Security dependency.

    Responsibilities:
    - Extract Bearer token
    - Delegate authentication to AuthService
    - Return authenticated user
    """

    try:
        user = auth_service.get_user_from_token(token)

        if not user.is_active:
            raise TokenError("Inactive user")

        return user

    except TokenError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )