
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from jose import jwt,JWTError
from core.config import get_settings
from core.cache.token_blacklist import is_token_blacklisted

from utils.exceptions import TokenError
import uuid

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
        "type": "access",         # Token type (access or refresh)
        "iat": now,               # Issued at(time token make)
        "exp": expire,            # Expiration
        "jti": str(uuid.uuid4()),  #unique token defnision
        "iss": settings.JWT_ISSUER,  # who issue token
        "aud": settings.JWT_AUDIENCE   # who has token
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM,
                      )

# ==========================================================
# Decode / Validate Token
# ==========================================================
def decode_and_verify_jwt(token: str) -> Dict:
    """
    decode and verify signayure.
    issuer , audience , and expiration

    Raises:
        TokenError: if token invalid or expired
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER
        )

    except JWTError:
        raise TokenError("Invalid or expired access token")
    
    jti = payload.get("jti")

    if jti and is_token_blacklisted(jti):
        raise TokenError("Token revoked")

    return payload
    

# =====================================
# internal verification helpers
# =====================================

def _verify_access_token_type(payload: dict) -> None:
    """
    Ensure token is an access token.
    """

    token_type = payload.get("type")

    if token_type != "access":
        raise TokenError("Invalid token type")
    