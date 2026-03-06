from utils.exceptions import WeakPasswordError

class PasswordPolicyService:
    """
    Password Policy Service

    Responsibility:
    - Define WHAT a strong password means
    - Decide when a password is rejected

    Important:
    - No hashing
    - No storage
    - No FastAPI
    - Pure business rules
    """

    MIN_LENGTH = 8

    def validate(self, password: str) -> None:
        """
        Validate password against security policy.

        Raises:
            WeakPasswordError: if password is not strong enough
        """

        if len(password) < self.MIN_LENGTH:
            raise WeakPasswordError("Password too short")

        if not any(c.isupper() for c in password):
            raise WeakPasswordError("Password must contain uppercase letter")

        if not any(c.islower() for c in password):
            raise WeakPasswordError("Password must contain lowercase letter")

        if not any(c.isdigit() for c in password):
            raise WeakPasswordError("Password must contain digit")

        if not any(not c.isalnum() for c in password):
            raise WeakPasswordError("Password must contain symbol")