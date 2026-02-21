from datetime import datetime,timezone
from core.enums.user_role import UserRole

class User:
    def __init__(
        self,
        id: int | None,
        username: str,
        email: str,
        password_hash: str,
        role: UserRole,
        is_active: bool = True,
        is_verified:bool= False,
        last_login_at:datetime|None=None,
        deleted_at:datetime |None= None,
        created_at: datetime | None = None,
    ):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active
        self.is_verified=is_verified
        self.last_login_at= last_login_at
        self.deleted_at=deleted_at
        self.created_at = created_at or datetime.now(timezone.utc)
    
    # ===== Representation =====
    

    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, username={self.username!r}, "
            f"email={self.email!r}, role={self.role.value}, "
            f"is_active={self.is_active}, is_verified={self.is_verified})"
        )