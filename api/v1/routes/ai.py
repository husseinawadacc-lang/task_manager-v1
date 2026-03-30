from fastapi import APIRouter, Depends

from services.ai_service import AIService
from api.deps.services_dep import get_ai_service
from api.schemas.ai import (AnalyzeTaskRequest, AnalyzeTaskResponse,
                             AISubtasksRequest,AISubtasksResponse )

from services.task_service import TaskService
from api.deps.services_dep import get_task_service
from api.deps.auth_dep import get_current_user_id

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/analyze-task", response_model=AnalyzeTaskResponse)
def analyze_task(
    request: AnalyzeTaskRequest,
    ai_service: AIService = Depends(get_ai_service),
):
    result = ai_service.analyze_task(request.text)
    return result

# 👇 endpoint جديد
@router.post("/create-task-from-ai")
def create_task_from_ai(
    request: AnalyzeTaskRequest,
    project_id: int,
    user_id: int = Depends(get_current_user_id),
    ai_service: AIService = Depends(get_ai_service),
    task_service: TaskService = Depends(get_task_service),
):
    """
    AI-powered task creation

    Flow:
    1️⃣ Analyze text using AI
    2️⃣ Create task using TaskService
    """

    # 1️⃣ AI analysis
    result = ai_service.analyze_task(request.text)

    # 2️⃣ Create task
    task = task_service.create_task(
        project_id=project_id,
        user_id=user_id,
        title=result["title"],
        description=result["description"],
        priority=result["priority"],
    )

    return task
@router.post("/suggest-subtasks",
             response_model=AISubtasksResponse)
def suggest_subtasks(input:AISubtasksRequest,
                     ai_service:AISubtasksRequest=Depends(get_ai_service),
                                              ):
    subtasks= AIService.generate_subtasks(input.title)
    return  {"subtasks" : subtasks}