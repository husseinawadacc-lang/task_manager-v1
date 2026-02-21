from typing import Optional
from core.enums.user_role import UserRole
from models.user import User
from storage.base_st import BaseStorage
from utils.security import hash_password, verify_password, validate_password_strength
from utils.exceptions import (
    AuthenticationError,
    ConflictError,
    WeakPasswordError,
)



class AuthService:
    """
    AuthService
    -----------
    This service contains ONLY authentication business logic.

    ❌ It knows NOTHING about:
        - HTTP
        - FastAPI
        - Request / Response
        - Headers
        - client_ip
        - rate limiting
        - JWT

    ✅ It knows about:
        - Users
        - Password rules
        - Authentication logic
        - Storage
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage
        
      
    # =====================================================
    # REGISTER
    # =====================================================
    def register(
        self,
        *,
        username: str,
        email: str,
        password: str,
        role: UserRole = UserRole.USER,
        is_active: bool = True,
    ) -> User:
        """
        Register a new user.

        Business rules:
        - Email must be unique
        - Password must meet security requirements
        - Password is always stored hashed
        """

        # 1️⃣ Check email uniqueness
        if self.storage.get_user_by_email(email):
            raise ConflictError("email already exists")

        # 2️⃣ Validate password strength (pure security rule)
        if not validate_password_strength(password):
            raise WeakPasswordError(
                "password does not meet security requirements"
            )

        # 3️⃣ Hash password (pepper from settings)
        password_hash = hash_password(
            password,)

        # 4️⃣ Create user entity
        user = User(
            id=None,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )

        # 5️⃣ Persist user
        self.storage.save_user(user)

        return user

    # =====================================================
    # LOGIN
    # =====================================================
    def login(self, *, email: str, password: str) -> User:
        """
        Authenticate a user by email & password.

        Business rules:
        - Email must exist
        - Password must match
        - User must be active
        """

        user = self.storage.get_user_by_email(email)

        if not user:
            raise AuthenticationError("invalid credentials")

        if not user.is_active:
            raise AuthenticationError("user is inactive")

        if not verify_password(
            password,
            user.password_hash,
                    ):
            raise AuthenticationError("invalid credentials")

        return user

    # =====================================================
    # GET USER BY ID
    # =====================================================
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieve user by ID.

        Used by:
        - Auth dependencies
        - Token decoding logic
        """

        return self.storage.get_user_by_id(user_id)