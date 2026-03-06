from fastapi import APIRouter, Depends, Request, status, HTTPException, Header
from api.deps.auth import get_current_user
from api.deps.services import (get_auth_service,get_password_reset_service,
                               get_token_service)
from api.schemas.user import (
    RegisterRequest,
    RegisterResponse,
    LoginResponse,UserResponse) 
from api.schemas.user import (loginRequest ,PasswordResetConfirmRequest,
PasswordResetRequest,)
from utils.rate_limiter import login_rate_limiter
from utils.logger import get_logger
from utils.exceptions import (
    AuthenticationError,
    TokenError,
    WeakPasswordError,)
from services.token_services import TokenService
from services.password_reset_services import PasswordResetService

router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger(__name__)


@router.get("/me",response_model=UserResponse)
def get_me(current_user = Depends(get_current_user)):
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
        raise HTTPException(status_code=400,detail=str(e))
    
    except TokenError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except WeakPasswordError as e:
        raise HTTPException(status_code=400, detail=str(e))

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

# =========================
# Login (json body)
# =========================
@router.post("/login", response_model=LoginResponse)
def login(
    data: loginRequest,
    request: Request,
    auth_service = Depends(get_auth_service),
    token_service :TokenService = Depends(get_token_service)
):
    """
    Login endpoint
    ----------------
    Responsibilities:
    - Rate limiting
    - Logging
    - Calling AuthService
    - Token generation
    - HTTP error mapping
    """

    # 1️⃣ Extract client IP
    client_ip = request.client.host if request.client else "unknown"

    # 2️⃣ Build rate limit key
    key = f"login:{client_ip}:{data.email}"

    # 3️⃣ Rate limit check (SECURITY)
    try:
        login_rate_limiter.check(key)
    except Exception:
        logger.warning(
            "Login rate limit exceeded",
            extra={
                "email": data.email,
                "ip": client_ip,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts, please try later",
        )
    
    # 4️⃣ Try authentication (BUSINESS LOGIC)
    try:
    
        user = auth_service.login(
            email=data.email,
            password=data.password,
        )
        
    except AuthenticationError as e:
    
        # 5️⃣ Failed login → record attempt

        login_rate_limiter.add_attempt(key)

        logger.info(
            "Login failed",
            extra={
                "email": data.email,
                "ip": client_ip,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # 6️⃣ Success → reset rate limiter
    login_rate_limiter.reset(key)

    # 7️⃣ Log success
    logger.info(
        "Login success",
        extra={
            "user_id": user.id,
            "ip": client_ip,
        },
    )
     # 8️⃣ issue tokens
    token_pair = token_service.issue_tokens(user)

    # 9️⃣ Response
    return LoginResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type=token_pair.token_type)


@router.post("/refresh", response_model=LoginResponse)
def refresh_token(
    authorization: str | None = Header(default=None),
    token_service: TokenService = Depends(get_token_service),
    
):
    # 1️⃣ تحقق من الهيدر
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    # 2️⃣ استخراج refresh token
    refresh_token = authorization.split(" ", 1)[1]

    # 3️⃣ استدعاء business logic
    token_pair=token_service.refresh_tokens(refresh_token=refresh_token)

    # 4️⃣ إرجاع response مطابق للـ schema
    return LoginResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type=token_pair.token_type)
