
from datetime import datetime, timezone

class Task:
    def __init__(
        self,
        id: int | None,
        owner_id: int,
        title: str,
        project_id: int,
        description: str = "",
        completed: bool = False,
        priority:str = "low",
        parent_id: int | None = None,
        subtasks: list["Task"] | None = None,
        completed_at: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        deleted_at: datetime | None = None,
    ):
        self.id = id
        self.owner_id = owner_id
        self.title = title
        self.project_id = project_id
        self.description = description or ""
        self.completed = completed
        self.priority =priority
        self.parent_id = parent_id
        self.subtasks = subtasks or []
        self.completed_at = completed_at
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at
        self.deleted_at = deleted_at




        # ==== reprensention ====    

    def __repr__(self)->str:
        return(
            f"Task(id={self.id},title ={self.title!r},"
            f"owner_id={self.owner_id},completed= {self.completed})")
            
        
