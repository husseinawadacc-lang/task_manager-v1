# domain/project.py

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Project:
    id: int | None = None   #id          → DB primary key
    name: str = ""          #name        → اسم المشروع
    owner_id: int = 0       #owner_id    → صاحب المشروع (security 🔥)
    created_at: datetime | None = None  #created_at  → وقت الإنشاء

    
