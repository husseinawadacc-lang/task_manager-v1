# utils/jwt_utils.py

from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from jose import jwt, JWTError
from core.config import  settings

# ==========================================================
# Exceptions
# ==========================================================

class TokenError(Exception):
    """
    Raised when a JWT token is invalid, expired, or malformed.
    """
    pass


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
# Refresh Token
# ==========================================================

def create_refresh_token(
    *,
    subject: str | int,
) -> str:
    """
    Create a REFRESH token.

    Refresh token:
    - Long-lived
    - Used ONLY to get a new access token
    - Never used to access protected resources directly

    Parameters:
    - subject: user identifier (usually user.id)
    """

    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload: Dict[str, Any] = {
        "sub": str(subject),
        "type": "refresh",        # Distinguish from access token
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ==========================================================
# Decode / Validate Token
# ==========================================================

def decode_token(
    *,
    token: str,
    expected_type: str | None = None,
) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Parameters:
    - token: raw JWT string
    - expected_type: optional ("access" or "refresh")

    Raises:
    - TokenError if token is invalid, expired, or wrong type
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

    except JWTError as exc:
        # Covers:
        # - expired token
        # - invalid signature
        # - malformed token
        raise TokenError("Invalid or expired token") from exc

    # Optional token type check
    if expected_type:
        token_type = payload.get("type")
        if token_type != expected_type:
            raise TokenError("Invalid token type")

    return payload