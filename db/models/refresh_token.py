"""
Refresh Token ORM model.

Stores refresh tokens for secure token rotation.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey

from datetime import datetime,timezone

from db.base import Base


class RefreshTokenORM(Base):
    """
    ORM model for refresh_tokens table.
    """

    __tablename__ = "refresh_tokens"

    # Primary key
    id = Column(Integer, primary_key=True)

    # Owner of token
    user_id = Column(Integer, ForeignKey("users.id"),index=True)

    # Hashed refresh token
    token_hash = Column(String,unique=True,index=True)

    # Expiration timestamp
    expires_at = Column(DateTime)

    # One-time usage flag
    used = Column(Boolean, default=False)

    # Creation time
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
