from pydantic import BaseModel, Field


class AnalyzeTaskRequest(BaseModel):
    text: str = Field(..., min_length=3, max_length=500)


class AnalyzeTaskResponse(BaseModel):
    title: str
    description: str
    priority: str

class AISubtasksRequest(BaseModel):
    title: str

class AISubtasksResponse(BaseModel):
    subtasks: list[str]        