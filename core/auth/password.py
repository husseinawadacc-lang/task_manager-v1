import hashlib
import hmac
from core.config import get_settings

settings = get_settings()


# =============================
# PASSWORD HASHING (مع pepper)
# =============================

def hash_password(password: str) -> str:
    """
    يحوّل كلمة السر إلى hash.
    نضيف pepper من settings لزيادة الأمان.
    """
    peppered = password + settings.PASSWORD_PEPPER
    return hashlib.sha256(peppered.encode()).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    """
    يقارن كلمة السر المدخلة مع المخزنة.
    """
    return hmac.compare_digest(
        hash_password(password),
        stored_hash
    )
