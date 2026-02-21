from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils.jwt_utils import decode_token
from services.auth_s import AuthService
from api.deps.services import get_auth_service
from utils.exceptions import AuthenticationError

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login")
def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Security dependency:
    - Extract Bearer token
    - Decode & validate JWT
    - Load user via AuthService
    - Return authenticated active user
    """

    try:
        # 1️⃣ Decode token (signature + exp)
        payload = decode_token(token=token)

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError()

        # 2️⃣ Load user (ONLY via service)
        user = auth_service.get_user_by_id(int(user_id))

        # 3️⃣ Validate user state
        if not user or not user.is_active:
            raise AuthenticationError()

        return user

    except AuthenticationError:
        # ⛔ Unified error → no enum attacks
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )