
from datetime import datetime, timezone

class Task:
    def __init__(
        self,
        id: int | None,
        owner_id: int,
        title: str,
        description: str = "",
        completed: bool = False,
        completed_at: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        deleted_at: datetime | None = None,
    ):
        self.id = id
        self.owner_id = owner_id
        self.title = title
        self.description = description or ""
        self.completed = completed
        self.completed_at = completed_at
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at
        self.deleted_at = deleted_at




        # ==== reprensention ====    

    def __repr__(self)->str:
        return(
            f"Task(id={self.id},title ={self.title!r},"
            f"owner_id={self.owner_id},completed= {self.completed})")
            
        
