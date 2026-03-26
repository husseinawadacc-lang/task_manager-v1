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

    id = Column(Integer, primary_key=True)

    title = Column(String, nullable=False)
    description = Column(String)

    # 🔥 ربط المستخدم
    owner_id = Column(Integer, ForeignKey("users.id"), index=True)

    # 🔥 ربط المشروع (الجديد)
    project_id = Column(Integer, ForeignKey("projects.id",ondelete="CASCADE"), index=True)

    completed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # 🔥 AI Priority
    priority = Column(String, default="low")

    # 🔥 Index مهم للأداء
    __table_args__ = (
        Index("ix_tasks_owner_project", "owner_id", "project_id"),
    )