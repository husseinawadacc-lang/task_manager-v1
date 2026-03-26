from fastapi import APIRouter, Depends, Request, status, HTTPException, Header,Response
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from api.deps.auth_dep import get_current_user,get_current_user_id
from api.deps.services_dep import (get_auth_service,get_password_reset_service,
                               get_token_service)
from api.schemas.user import (
    RegisterRequest,
    RegisterResponse,
    LoginResponse,UserResponse) 
from domain.user import User
from api.schemas.user import (loginRequest ,PasswordResetConfirmRequest,
PasswordResetRequest,)
from core.security. rate_limiter import login_rate_limiter
from utils.logger import get_logger
from utils.exceptions import (
    AuthenticationError,
    TokenError,
    WeakPasswordError,ValidationError,RateLimitError)
from services.token_services import TokenService
from services.password_reset_services import PasswordResetService
from core.auth.jwt import decode_and_verify_jwt
from core.cache.token_blacklist import blacklist_token
import time



router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger(__name__)
security = HTTPBearer()

@router.get("/me",response_model=UserResponse)
def get_me(current_user:User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role= current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

@router.post("/password-reset/request")
def password_reset_request(
    data: PasswordResetRequest,
    reset_service:PasswordResetService = Depends(get_password_reset_service),
):   
    # Enumeration-safe always
    reset_service.request_reset(data.email)

    return {
        "message": "If the email exists, a reset link has been sent."
    }

@router.post("/password-reset/confirm",
                          )
def password_reset_confirm(
    data: PasswordResetConfirmRequest,
    reset_service:PasswordResetService = Depends(get_password_reset_service),
):
    try:
        reset_service.confirm_reset(
            token=data.token,
            password=data.password,
        )

    except ValueError as e:
        raise ValidationError(str(e))
    
    return {"message": "Password reset successful"}
#=========================
# Register
# =========================

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    auth_service = Depends(get_auth_service),
):
    """
    Register endpoint

    Responsibilities:
    - Call AuthService.register
    - Translate business errors to HTTP
    """
    user = auth_service.register(
    email=data.email,
    password=data.password,
                )

    return RegisterResponse(id=user.id,email=user.email)

@router.post("/login", response_model=LoginResponse)
def login(
    data: loginRequest,
    request: Request,
    auth_service = Depends(get_auth_service),
    token_service: TokenService = Depends(get_token_service)
):
    """
    Login Endpoint

    Responsibilities:
    - Apply rate limiting
    - Authenticate user
    - Issue tokens
    - Log security events
    """

    # =========================================
    # 1️⃣ Extract client IP
    # =========================================
    client_ip = request.client.host if request.client else "unknown"

    # =========================================
    # 2️⃣ Build rate limit key
    # =========================================
    key = f"login:{client_ip}:{data.email}"

    # =========================================
    # 3️⃣ Rate limiting (check + add)
    # =========================================
    try:
        login_rate_limiter.check_and_add(key)

    except RateLimitError:
        logger.warning(
            "Login rate limit exceeded",
            extra={
                "email": data.email,
                "ip": client_ip,
            },
        )
        raise RateLimitError("Too many login attempts, please try later")

    # =========================================
    # 4️⃣ Authenticate
    # =========================================
    try:
        user = auth_service.login(
            email=data.email,
            password=data.password,
        )

    except AuthenticationError:
        logger.info(
            "Login failed",
            extra={
                "email": data.email,
                "ip": client_ip,
            },
        )
        raise AuthenticationError("Invalid email or password")

    # =========================================
    # 5️⃣ Log success
    # =========================================
    logger.info(
        "Login success",
        extra={
            "user_id": user.id,
            "ip": client_ip,
        },
    )

    # =========================================
    # 6️⃣ Issue tokens
    # =========================================
    token_pair = token_service.issue_tokens(user.id)

    # =========================================
    # 7️⃣ Response
    # =========================================
    return LoginResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type=token_pair.token_type,
    )

@router.post("/refresh", response_model=LoginResponse)
def refresh_token(
    authorization: str | None = Header(default=None),
    token_service: TokenService = Depends(get_token_service),
    
):
    # 1️⃣ تحقق من الهيدر
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationError("Not authenticated")

    # 2️⃣ استخراج refresh token
    refresh_token = authorization.split(" ", 1)[1]

    # 3️⃣ استدعاء business logic
    token_pair=token_service.refresh_tokens(refresh_token=refresh_token)

    # 4️⃣ إرجاع response مطابق للـ schema
    return LoginResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type=token_pair.token_type)


@router.post("/logout", status_code=204)
def logout(
    credentials:HTTPAuthorizationCredentials=Depends(security),
    token_service: TokenService = Depends(get_token_service),
):
    """
    Logout endpoint

    Security goals
    --------------
    1️⃣ Invalidate current access token (JWT blacklist)
    2️⃣ Revoke refresh token family
    """

    token = credentials.credentials

    try:
        # =====================================================
        # 2️⃣ Decode token (single source of truth)
        # =====================================================
        payload = decode_and_verify_jwt(token)

        jti = payload.get("jti")
        exp = payload.get("exp")

        # =====================================================
        # 3️⃣ Blacklist access token
        # =====================================================
        if jti and exp:
            ttl = max(exp - int(time.time()), 1)

            blacklist_token(jti, ttl)

    except TokenError:
        # 🔥 حتى لو التوكن invalid → نكمل revoke refresh
        pass

    # =====================================================
    # 4️⃣ Revoke refresh tokens
    # =====================================================
    token_service.logout(token)

    return Response(status_code=204)


@router.post("/logout-all", status_code=204)
def logout_all(
    current_user_id: int = Depends(get_current_user_id),
    token_service: TokenService = Depends(get_token_service),
):
    """
    Logout from all devices.
    """

    token_service.logout_all(current_user_id)

    return Response(status_code=204)
