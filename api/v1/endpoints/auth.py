from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from api.deps.auth import get_current_user
from api.schemas.user import (
    RegisterRequest,
    RegisterResponse,
    LoginResponse) 
from api.schemas.user import loginRequest 
from api.deps.services import get_auth_service
from services.auth_s import AuthService
from models.user import User
from utils.jwt_utils import create_access_token, create_refresh_token
from utils.rate_limiter import login_rate_limiter
from utils.logger import get_logger
from utils.exceptions import (
    ConflictError,
    WeakPasswordError,
    AuthenticationError,
)
from fastapi import HTTPException
router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger(__name__)



@router.get("/me")
def get_me(current_user:User = Depends(get_current_user)):
    return current_user

# =========================
# Register
# =========================

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Register endpoint

    Responsibilities:
    - Call AuthService.register
    - Translate business errors to HTTP
    """

    try:
        user = auth_service.register(
            username=data.username,
            email=data.email,
            password=data.password,
            role=data.role,
        )

        return RegisterResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
        )

    except ConflictError as e:
        # Email already exists
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(e)},
        )

    except WeakPasswordError as e:
       return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(e)},
        )

# =========================
# Login (json body)
# =========================
@router.post("/login", response_model=LoginResponse)
def login(
    data: loginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
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
    except AuthenticationError:
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
     # 8️⃣ Generate tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    # 9️⃣ Response
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )
