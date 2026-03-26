from fastapi import APIRouter
from api.v1.routes import auth,tasks,project,health

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(tasks.router)
api_router.include_router(project.router)
api_router.include_router(health.router)

