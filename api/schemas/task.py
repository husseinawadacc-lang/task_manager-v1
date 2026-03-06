from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str|None = Field(default=None, max_length=1000)


class TaskUpdateRequest(BaseModel):
    title :str|None = Field(default=None, min_length=1, max_length=200)
    description: str|None= Field(None, max_length=1000)
    completed: bool|None= None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str|None
    completed: bool
    owner_id: int
    created_at:datetime

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    items:List[TaskResponse]
    total:int
    limit:int
    offset:int        