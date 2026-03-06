"""
Task ORM model.

يمثل جدول tasks في PostgreSQL.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey,Index

from datetime import datetime,timezone

from db.base import Base


class TaskORM(Base):
    """
    ORM model for tasks table.
    """

    __tablename__ = "tasks"

    # Primary key
    id = Column(Integer, primary_key=True)

    # Task title
    title = Column(String, nullable=False)

    # Task description
    description = Column(String)

    # Owner of the task
    owner_id = Column(Integer, ForeignKey("users.id"), index=True)

    # Task completion status
    completed = Column(Boolean, default=False)

    # Creation timestamp
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
