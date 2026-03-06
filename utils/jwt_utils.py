# utils/jwt_utils.py

from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from jose import jwt,JWTError
from core.config import get_settings
from utils.exceptions import TokenError


settings = get_settings()
# ==========================================================
# Access Token
# ==========================================================

def create_access_token(
    *,
    subject: str | int,
    
) -> str:
    """
    Create an ACCESS token.

    Access token:
    - Short-lived
    - Used on every authenticated request
    - Stored in Authorization header (Bearer)

    Parameters:
    - subject: user identifier (usually user.id)
    """

    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": str(subject),      # Subject (user id)
        "type": "access",         # Token type
        "iat": now,               # Issued at
        "exp": expire,            # Expiration
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# ==========================================================
# Decode / Validate Token
# ==========================================================
def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Validate and decode access token.

    Raises:
        TokenError: if token invalid or expired
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

    except JWTError:
        raise TokenError("Invalid or expired access token")

    if payload.get("type") != "access":
        raise TokenError("Invalid token type")

    return payload

