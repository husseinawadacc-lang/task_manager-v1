# utils/reset_token_utils.py

import secrets
import hashlib


def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def verify_reset_token(raw_token: str, hashed_token: str) -> bool:
    return hash_reset_token(raw_token) == hashed_token