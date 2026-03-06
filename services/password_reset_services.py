from datetime import datetime, timedelta, timezone
from storage.base_st import BaseStorage
from services.password_policy_s import PasswordPolicyService
from utils.security import (
    generate_reset_token,
    hash_reset_token,
    hash_password,)
from utils.exceptions import TokenError,NotFoundError
from services.unit_of_work import UnitOfWork

class PasswordResetService:
    """
    Password Reset Service (Use Case)

    Responsibility:
    - Handle password reset token lifecycle
    - Enforce expiration & one-time usage
    - Delegate password strength validation to PasswordPolicyService
    - Update password securely

    Does NOT:
    - Know anything about AuthService
    - Know HTTP / FastAPI
    - Know JWT / sessions
    """

    RESET_TOKEN_EXPIRE_MINUTES = 30

    def __init__(self, storage:BaseStorage, password_policy: PasswordPolicyService,uow):
        self.storage = storage
        self.password_policy = password_policy
        self.uow=uow
    # --------------------------------------------------
    # REQUEST PASSWORD RESET
    # --------------------------------------------------
    def request_reset(self, email: str) -> None:
        """
        Request password reset.

        Security rules:
        - Enumeration safe (silent if user does not exist)
        - Token is generated securely
        - Only hashed token is stored
        """
        
        # 1️⃣ Try to find user (silent fail if not exists)
        try:
            with self.uow as session:
                user = self.storage.get_user_by_email(email=email,session=session)
                        
                # 2️⃣ Generate raw token (never stored)
                raw_token = generate_reset_token()

                # 3️⃣ Hash token before storage
                token_hash = hash_reset_token(raw_token)

                # 4️⃣ Compute expiration
                expires_at = datetime.now(timezone.utc) + timedelta(
                    minutes=self.RESET_TOKEN_EXPIRE_MINUTES
                )

                # 5️⃣ Persist reset token
                self.storage.create_password_reset_token(
                    user_id=user.id,
                    token_hash=token_hash,
                    expires_at=expires_at,
                    session=session
                )

        except NotFoundError:
            # enumeration safe
            return

        # NOTE:
        # Sending email is intentionally outside this service

    # --------------------------------------------------
    # CONFIRM PASSWORD RESET
    # --------------------------------------------------
    def confirm_reset(self, token: str, password: str) -> None:
        """
        Confirm password reset.

        Steps:
        1. Validate password policy
        2. Validate token existence
        3. Validate token expiration
        4. Validate token not used
        5. Update password
        6. Mark token as used
        """

        # 1️⃣ Validate password policy
        self.password_policy.validate(password)

        # 2️⃣ Hash incoming token
        token_hash = hash_reset_token(token)

        # 3️⃣ Start transaction
        with self.uow as session:

            try:
                # 4️⃣ Load token record
                record = self.storage.get_password_reset_token(
                    session=session,
                    token_hash=token_hash
                )

            except NotFoundError:
                raise TokenError("Reset token not found")

            # 5️⃣ Check if already used
            if record.used:
                raise TokenError("Reset token already used")

            # 6️⃣ Check expiration
            if record.expires_at < datetime.now(timezone.utc):
                raise TokenError("Reset token expired")

            # 7️⃣ Hash new password
            password_hash = hash_password(password)

            # 8️⃣ Update password
            self.storage.update_user_password(
                session=session,
                user_id=record.user_id,
                password_hash=password_hash,
            )

            # 9️⃣ Mark token used
            self.storage.mark_password_reset_token_used(
                session=session,
                token_id=record.id
            )