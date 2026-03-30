"""
Task ORM model.

يمثل جدول tasks في PostgreSQL.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey,Index
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from db.base import Base

class TaskORM(Base):
    """
    ORM model for tasks table.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)

    title = Column(String, nullable=False)

    description = Column(String)

    owner_id = Column(Integer, ForeignKey("users.id"), index=True)

    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), index=True)

    # 🔥 Subtasks
    parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=True, index=True)

    completed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    priority = Column(String, default="low")

    # 🔥 Relationship

    parent = relationship("TaskORM",remote_side=[id], back_populates="subtasks")

    subtasks = relationship("TaskORM",back_populates="parent",cascade="all, delete-orphan")

    __table_args__ = ( Index("ix_tasks_owner_project", "owner_id", "project_id"),    )