from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from db.base import Base


class ProjectMemberORM(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id",ondelete=("CASCADE")),
        nullable=False,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    role = Column(String, default="member")  # owner / member

    created_at = Column(
        DateTime,
        default=datetime.now(timezone.utc)
    )