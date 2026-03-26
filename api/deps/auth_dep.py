"""
auth_dep.py

🔥 المسؤوليات:
- استخراج المستخدم من JWT
- فرض authentication على endpoints
- تحويل أي TokenError → HTTP 401

🔥 مبدأ مهم:
❗ لا نعمل decode هنا
✔ كل التحقق يتم داخل jwt.py + token_service
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.auth_service import AuthService
from services.token_services import TokenService

from api.deps.services_dep import get_auth_service, get_token_service

from utils.exceptions import TokenError
from domain.user import User


# ==========================================================
# Security Scheme (Bearer Token)
# ==========================================================

# 🔐 FastAPI هيتعامل مع Authorization: Bearer <token>
security = HTTPBearer()


# ==========================================================
# Get Current User (Full user object)
# ==========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    🔥 الهدف:
    استخراج المستخدم الحالي من التوكن

    =====================================================
    🔄 Flow النهائي (بعد الإصلاح)
    =====================================================

    1️⃣ استخراج التوكن من header
    2️⃣ تمرير التوكن إلى AuthService
    3️⃣ AuthService →
        → TokenService →
            → decode_and_verify_jwt (🔥 هنا كل السحر)
                ✔ verify signature
                ✔ check expiration
                ✔ check blacklist (logout)
                ✔ verify token type
    4️⃣ استخراج user_id
    5️⃣ تحميل المستخدم من DB
    6️⃣ التأكد إنه active
    7️⃣ إرجاع user

    =====================================================
    ❗ مهم جدًا:
    ❌ لا نعمل decode هنا
    ❌ لا نعمل blacklist check هنا
    ✔ كل ده يتم في jwt.py فقط
    =====================================================
    """

    token = credentials.credentials

    try:
        # 🔥 كل validation بيحصل تحت (token_service + jwt.py)
        user = auth_service.get_user_from_token(token)

        # 🛑 منع المستخدم غير المفعل
        if not user.is_active:
            raise TokenError("Inactive user")

        return user

    except TokenError:
        # 🔴 أي مشكلة في التوكن → Unauthorized
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ==========================================================
# Get Current User ID (Lightweight)
# ==========================================================

def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token_service: TokenService = Depends(get_token_service),
) -> int:
    """
    🔥 الهدف:
    استخراج user_id فقط بدون تحميل user من DB

    =====================================================
    🔄 Flow
    =====================================================

    1️⃣ استخراج التوكن
    2️⃣ تمريره إلى TokenService
    3️⃣ TokenService →
        → decode_and_verify_jwt
            ✔ signature
            ✔ expiration
            ✔ blacklist (🔥 logout check)
            ✔ token type
    4️⃣ استخراج user_id (sub)
    5️⃣ إرجاعه

    =====================================================
    💡 يستخدم في:
    - endpoints performance-critical
    - لما مش محتاج user كامل
    =====================================================
    """

    token = credentials.credentials

    try:
        # 🔥 نفس source of truth
        user_id = token_service.validate_access_token(token)

        return user_id

    except TokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )