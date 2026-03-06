"""
User ORM model.

يمثل جدول users في قاعدة البيانات PostgreSQL.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime,Index
from datetime import datetime,timezone
from db.base import Base


class UserORM(Base):
    """
    ORM model for users table.
    """

    __tablename__ = "users"

    # Primary Key
    id = Column(Integer, primary_key=True)

    # User email (unique)
    email = Column(String, unique=True, nullable=False, index=True)

    # Password hash
    password_hash = Column(String, nullable=False)

    # Role (user / admin)
    role = Column(String, nullable=False)

    # Account active flag
    is_active = Column(Boolean, default=True)

    # created at column
    created_at = Column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),
                        nullable=False)
