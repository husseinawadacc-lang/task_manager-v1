from pydantic import BaseModel
from datetime import datetime


class ProjectCreateRequest(BaseModel):
    name: str


class ProjectResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime