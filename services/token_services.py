from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from core.config import get_settings
from core.auth.jwt import create_access_token, decode_and_verify_jwt,_verify_access_token_type
from core.auth.token import generate_refresh_token, hash_token
from utils.exceptions import TokenError, NotFoundError, AuthenticationError
from storage.base_st import BaseStorage
from services.unit_of_work import UnitOfWork
from core.cache.token_blacklist import is_token_blacklisted
from utils.logger import get_logger
import secrets

settings = get_settings()
logger = get_logger(__name__)

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
            
            family_id =secrets.token_hex(16)

            return self._issue_tokens(
                session=session,
                user_id=user_id,
                family_id=family_id
            )


# ============================================================
# Internal Token Creation (shared logic)
# ============================================================

    def _issue_tokens(self, *, session, user_id: int,family_id:str) -> TokenPair:
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
        token_hash = hash_token(raw_refresh_token)

        # 4️⃣ Compute expiration time
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        # 5️⃣ Store token hash in database
        self.storage.create_refresh_token(
            session=session,
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            family_id= family_id
        )
        logger.info(
                    "Tokens issued",
                    extra={"user_id": user_id} )
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
        token_hash = hash_token(refresh_token)

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
            if record.revoked :
                raise AuthenticationError("invalid refresh token")    
            # 6️⃣ Issue new token pair
            
            if record.used:
                logger.warning(
                            "Refresh token reuse detected",
                            extra={"user_id": record.user_id} )
                self.storage.revoke_token_family(
                    session=session,
                    family_id=record.family_id)
                raise AuthenticationError("invalid refresh token")
            
            # 4️⃣ Enforce expiration
            if record.expires_at < datetime.now(timezone.utc):
                raise AuthenticationError("invalid refresh token")
            

            # 5️⃣ Mark old refresh token used
            self.storage.mark_refresh_token_used(
                session=session,
                token_id=record.id
            )
            logger.info(
                            "Refresh token rotated",
                            extra={"user_id": record.user_id} )
            
            return self._issue_tokens(
                session=session,
                user_id=record.user_id,
                family_id=record.family_id
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

        Flow:
        -----
        ✔ decode JWT (includes signature + exp + blacklist)
        ✔ verify token type
        ✔ extract user_id
        """

        # 🔥 مصدر واحد للتحقق (يشمل blacklist)
        payload = decode_and_verify_jwt(token)

        # ✔ تأكد إنه access token
        _verify_access_token_type(payload)

        # ✔ استخراج user_id
        user_id = payload.get("sub")

        if not user_id:
            raise TokenError("Invalid access token payload")

        return int(user_id)


    def revoke_refresh_token(self, raw_token: str) -> None:

        token_hash = hash_token(raw_token)

        with self.uow as session:

            try:
                record = self.storage.get_refresh_token(
                    session=session,
                    token_hash=token_hash
                )

            except NotFoundError:
                return

            self.storage.revoke_refresh_token(
                session=session,
                token_id=record.id
            )

            logger.info(
                "Refresh token revoked",
                extra={"user_id": record.user_id}
            )


    def revoke_token_family(self, family_id: str) -> None:

        with self.uow as session:

            self.storage.revoke_token_family(
                session=session,
                family_id=family_id
            )

            logger.info(
                "Token family revoked",
                extra={"family_id": family_id}
            )
    
    def logout(self, refresh_token: str) -> None:

        token_hash = hash_token(refresh_token)

        with self.uow as session:

            try:
                record = self.storage.get_refresh_token(
                    session=session,
                    token_hash=token_hash
                )

            except NotFoundError:
                return

            self.storage.revoke_token_family(
                session=session,
                family_id=record.family_id
            )

            logger.info(
                "User logout",
                extra={"user_id": record.user_id}
            )


    def logout_all(self, user_id: int) -> None:
        """
        Logout user from ALL devices.

        Security behaviour
        ------------------
        This function revokes every refresh token belonging to the user.

        Result:
        -------
        - User cannot refresh tokens anymore
        - All sessions become invalid once access tokens expire

        Typical use cases:
        ------------------
        1️⃣ User chooses "Logout from all devices"
        2️⃣ Password change
        3️⃣ Security incident
        4️⃣ Admin revokes sessions
        """

        # UnitOfWork manages the transaction lifecycle.
        # Storage MUST NOT commit transactions itself.
        with self.uow as session:

            # revoke all refresh tokens for the user
            self.storage.revoke_tokens_by_user(
                session=session,
                user_id=user_id
            )

            # security log
            logger.info(
                "All user sessions revoked",
                extra={"user_id": user_id}
            )        