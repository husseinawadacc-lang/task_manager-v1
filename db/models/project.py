# db/models/project.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,UniqueConstraint
from datetime import datetime, timezone
from db.base import Base

class ProjectORM(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        index=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.now(timezone.utc)
    )

    # 🔥 أهم إضافة
    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="uq_user_project_name"),
    )