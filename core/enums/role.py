from enum import Enum

class UserRole(str,Enum):
    USER ="user"
    ADMIN ="admin"

    def is_admin(self):
        return self == UserRole.ADMIN