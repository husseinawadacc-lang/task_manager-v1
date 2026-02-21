import os
import re
import hashlib
import hmac
from core.config import settings
# =========================
# Security Constants
# ==========================


ITERATIONS = 200_000        # زيادة القوة
SALT_SIZE = 16              # 16 bytes salt


# =========================
# Password Policy Validation
# =========================

def validate_password_strength(password: str) -> bool:
    """
    Enforces strong password rules.
    Returns True if password is strong, False otherwise.
    """

    if not isinstance(password, str):
        return False

    if len(password) < 8:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"[0-9]", password):
        return False

    if not re.search(r"[!@#$%^&*()_\-+=<>?]", password):
        return False

    return True


# =========================
# Hash Password
# =========================

def hash_password(password: str) -> str:
    """
    Securely hashes password using PBKDF2-HMAC-SHA256.
    Returns format: salt:hash
    """

    validate_password_strength(password)

    # Add pepper before hashing
    password = password + settings.PASSWORD_PEPPER

    salt = os.urandom(SALT_SIZE)

    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS
    )

    return f"{salt.hex()}:{hash_bytes.hex()}"


# =========================
# Verify Password
# =========================

def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verifies password against stored hash.
    Uses constant-time comparison to prevent timing attacks.
    """

    try:
        salt_hex, hash_hex = stored_hash.split(":")

        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)

        password = password + settings.PASSWORD_PEPPER

        new_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            ITERATIONS
        )

        return hmac.compare_digest(new_hash, expected_hash)

    except Exception:
        # Never reveal details
        return False