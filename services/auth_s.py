from core.enums.user_role import UserRole
from models.user import User

from storage.base_st import BaseStorage

from utils.security import (
    hash_password,
    verify_password,
)

from services.password_policy_s import PasswordPolicyService
from services.unit_of_work import UnitOfWork

from utils.exceptions import (
    ConflictError,
    AuthenticationError,
    NotFoundError,
)


class AuthService:
    """
    AuthService
    ===========

    This service contains ONLY authentication business logic.

    The service layer is responsible for:
        - business rules
        - translating storage errors
        - coordinating operations

    This service DOES NOT know anything about:
        - HTTP
        - FastAPI
        - JWT
        - rate limiting
    """

    def __init__(
        self,
        storage: BaseStorage,
        password_policy: PasswordPolicyService,
        uow: UnitOfWork,
        token_service,
    ):
        self.storage = storage
        self.password_policy = password_policy
        self.uow = uow
        self.token_service=token_service
    # =====================================================
    # REGISTER
    # =====================================================

    def register(
        self,
        *,
        email: str,
        password: str,
    ) -> User:
        """
        Register a new user.

        Business rules:
        - email must be unique
        - password must satisfy password policy
        - password must be stored hashed
        """

        # ==================================================
        # 1️⃣ Start transaction
        # ==================================================

        with self.uow as session:

            # ==================================================
            # 2️⃣ Check email uniqueness
            # ==================================================
            # Storage throws NotFoundError if user does not exist.
            # That is the normal path for registration.
            # ==================================================

            try:
                self.storage.get_user_by_email(
                    session=session,
                    email=email,
                )

                # If we reach here → user exists
                raise ConflictError("Email already registered")

            except NotFoundError:
                # Expected case: user does not exist
                pass

            # ==================================================
            # 3️⃣ Validate password policy
            # ==================================================

            self.password_policy.validate(password)

            # ==================================================
            # 4️⃣ Hash password
            # ==================================================

            password_hash = hash_password(password)

            # ==================================================
            # 5️⃣ Create domain user object
            # ==================================================

            user = User(
                id=None,
                email=email,
                password_hash=password_hash,
                role=UserRole.USER,
                is_active=True,
            )

            # ==================================================
            # 6️⃣ Persist user using storage
            # ==================================================
            # Storage performs ONLY database operations.
            # No commit happens here.
            # Commit is handled by UnitOfWork.
            # ==================================================

            user = self.storage.create_user(
                session=session,
                user=user,
            )

            return user

    # =====================================================
    # LOGIN
    # =====================================================

    def login(
        self,
        *,
        email: str,
        password: str,
    ) -> User:
        """
        Authenticate user.

        Security rules:
        - Do NOT reveal if email exists
        - Do NOT reveal account status
        - Always return generic authentication error
        """

        with self.uow as session:

            # ==================================================
            # 1️⃣ Fetch user
            # ==================================================

            try:
                user = self.storage.get_user_by_email(
                    session=session,
                    email=email,
                )

            except NotFoundError:
                # Prevent user enumeration attack
                raise AuthenticationError("Invalid credentials")

            # ==================================================
            # 2️⃣ Verify password
            # ==================================================

            if not verify_password(password, user.password_hash):
                raise AuthenticationError("Invalid credentials")

            # ==================================================
            # 3️⃣ Check account status
            # ==================================================

            if not user.is_active:
                raise AuthenticationError("Account disabled")

            # ==================================================
            # 4️⃣ Authentication success
            # ==================================================

            return user

    # =====================================================
    # GET USER BY ID
    # =====================================================

    def get_user_by_id(
        self,
        *,
        user_id: int,
    ) -> User:
        """
        Retrieve user by id.

        Used by:
        - auth dependency
        - token validation
        """

        with self.uow as session:

            return self.storage.get_user_by_id(
                session=session,
                user_id=user_id,
            )
        
    def get_user_from_token(self, token: str) -> User:
        """
        Resolve user from access token.
        """

        user_id = self.token_service.validate_access_token(token)

        with self.uow as session:

            user = self.storage.get_user_by_id(
                session=session,
                user_id=user_id
            )

        return user    