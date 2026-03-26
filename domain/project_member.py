from dataclasses import dataclass


@dataclass
class ProjectMember:
    """
    Represents membership of a user in a project.
    """

    user_id: int
    project_id: int
    role: str  # admin / member / viewer