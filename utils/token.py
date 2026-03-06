import secrets
import hashlib


def generate_refresh_token() -> str:
    """
    Generate a cryptographically secure random refresh token.

    - High entropy
    - URL-safe
    - Not a JWT
    """
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    """
    Hash refresh token before storage.

    Same philosophy as password hashing:
    - Never store raw tokens
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()