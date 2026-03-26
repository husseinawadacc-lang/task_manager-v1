"""
Token Utilities

Centralized utilities for secure token generation,
hashing, and verification.

Used for:
- Refresh tokens
- Password reset tokens

Security principles:
1. Tokens are generated using cryptographically secure randomness.
2. Raw tokens are NEVER stored in the database.
3. Only hashed tokens are stored.
4. Verification is performed using constant-time comparison.
"""

import secrets
import hashlib
import hmac

from core.config import get_settings

settings = get_settings()


# =========================================================
# TOKEN CONSTANTS
# =========================================================

RESET_TOKEN_LENGTH = 32
REFRESH_TOKEN_LENGTH = 64


# =========================================================
# CORE TOKEN FUNCTIONS
# =========================================================

def generate_token(length: int = RESET_TOKEN_LENGTH) -> str:
    """
    Generate a secure random token.

    Args:
        length: entropy size of the token.

    Returns:
        URL-safe random token.
    """
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    """
    Hash a token before storing it in the database.

    Uses HMAC + SHA256 with the application SECRET_KEY.
    This prevents rainbow table attacks and binds
    the hash to this specific application.
    """
    token=str(token)
    return hmac.new(
        settings.SECRET_KEY.encode(),
        token.encode(),
        hashlib.sha256,
    ).hexdigest()


def verify_token(raw_token: str, stored_hash: str) -> bool:
    """
    Verify that the provided token matches the stored hash.

    Uses constant-time comparison to prevent timing attacks.
    """

    calculated_hash = hash_token(raw_token)

    return hmac.compare_digest(calculated_hash, stored_hash)


# =========================================================
# SPECIALIZED TOKEN HELPERS
# =========================================================

def generate_refresh_token() -> str:
    """
    Generate a refresh token.

    Refresh tokens are longer because they live longer
    and must be harder to guess.
    """
    return generate_token(REFRESH_TOKEN_LENGTH)


def generate_reset_token() -> str:
    """
    Generate a password reset token.

    Reset tokens are shorter because they expire quickly.
    """
    return generate_token(RESET_TOKEN_LENGTH)