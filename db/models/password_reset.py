"""
Password Reset Token ORM model.

Used for secure password reset flow.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime,timezone

from db.base import Base


class PasswordResetTokenORM(Base):
    """
    ORM model for password_reset_tokens table.
    """

    __tablename__ = "password_reset_tokens"

    # Primary key
    id = Column(Integer, primary_key=True)

    # User who requested reset
    user_id = Column(Integer, ForeignKey("users.id"),index=True)

    # Hashed reset token
    token_hash = Column(String, unique=True,index=True)

    # Expiration timestamp
    expires_at = Column(DateTime)

    # One-time use
    used = Column(Boolean, default=False)

    # Creation timestamp
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
