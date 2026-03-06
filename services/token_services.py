from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from core.config import get_settings
from utils.jwt_utils import create_access_token, decode_access_token
from utils.token import generate_refresh_token, hash_refresh_token
from utils.exceptions import TokenError, NotFoundError, AuthenticationError
from storage.base_st import BaseStorage
from services.unit_of_work import UnitOfWork


settings = get_settings()


# ============================================================
# Value Object
# ============================================================

@dataclass(frozen=True)
class TokenPair:
    """
    Immutable object representing issued tokens.

    Why dataclass?
    --------------
    - Clear structure
    - Immutable (frozen=True)
    - Easy to return from service
    - Perfect for FastAPI response_model
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ============================================================
# Token Service
# ============================================================

class TokenService:
    """
    TokenService

    Responsible for:

    1️⃣ Issuing tokens during login
    2️⃣ Rotating refresh tokens
    3️⃣ Validating access tokens

    Important rules:
    ----------------
    - Does NOT know HTTP
    - Does NOT raise HTTPException
    - Only raises domain exceptions

    Architecture:
    -------------
    API
      ↓
    TokenService
      ↓
    UnitOfWork
      ↓
    Storage
      ↓
    Database
    """

    def __init__(self, storage: BaseStorage, uow: UnitOfWork):
        self.storage = storage
        self.uow = uow


# ============================================================
# Issue Tokens (Login)
# ============================================================

    def issue_tokens(self, user_id: int) -> TokenPair:
        """
        Create access + refresh tokens for a user.

        Used during:
        - Login

        Steps:
        ------
        1️⃣ create access token
        2️⃣ generate random refresh token
        3️⃣ hash refresh token
        4️⃣ store hash in database
        5️⃣ return raw refresh token to client
        """

        with self.uow as session:

            return self._issue_tokens(
                session=session,
                user_id=user_id
            )


# ============================================================
# Internal Token Creation (shared logic)
# ============================================================

    def _issue_tokens(self, *, session, user_id: int) -> TokenPair:
        """
        Internal helper.

        Why this function exists:
        -------------------------
        To avoid nested transactions when refresh_tokens()
        calls token creation.

        It uses the SAME session.
        """

        # 1️⃣ Create short-lived access token (JWT)
        access_token = create_access_token(subject=user_id)

        # 2️⃣ Generate secure random refresh token
        raw_refresh_token = generate_refresh_token()

        # 3️⃣ Hash refresh token before storing
        token_hash = hash_refresh_token(raw_refresh_token)

        # 4️⃣ Compute expiration time
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        # 5️⃣ Store token hash in database
        self.storage.create_refresh_token(
            session=session,
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )

        # 6️⃣ Return tokens to client
        return TokenPair(
            access_token=access_token,
            refresh_token=raw_refresh_token,
        )


# ============================================================
# Refresh Token Rotation
# ============================================================

    def refresh_tokens(self, *, refresh_token: str) -> TokenPair:
        """
        Rotate refresh token.

        Security rules:
        ---------------
        - Token must exist
        - Token must not be used
        - Token must not be expired
        - Old token becomes invalid
        - New token pair issued
        """

        # 1️⃣ Hash incoming refresh token
        token_hash = hash_refresh_token(refresh_token)

        with self.uow as session:

            # 2️⃣ Load refresh token record
            try:
                record = self.storage.get_refresh_token(
                    session=session,
                    token_hash=token_hash
                )

            except NotFoundError:
                raise AuthenticationError("invalid refresh token")

            # 3️⃣ Prevent reuse
            if record.used:
                raise AuthenticationError("invalid refresh token")

            # 4️⃣ Enforce expiration
            if record.expires_at < datetime.now(timezone.utc):
                raise AuthenticationError("invalid refresh token")

            # 5️⃣ Mark old refresh token used
            self.storage.mark_refresh_token_used(
                session=session,
                token_id=record.id
            )

            # 6️⃣ Issue new token pair
            return self._issue_tokens(
                session=session,
                user_id=record.user_id
            )


# ============================================================
# Validate Access Token
# ============================================================

    def validate_access_token(self, token: str) -> int:
        """
        Validate access token.

        Returns:
        --------
        user_id

        This function:
        - verifies JWT
        - extracts subject
        """

        try:
            payload = decode_access_token(token)

        except TokenError:
            raise TokenError("Invalid access token")

        user_id = payload.get("sub")

        if not user_id:
            raise TokenError("Invalid access token payload")

        return int(user_id)