from fastapi import APIRouter
from api.v1.endpoints import auth,tasks

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(tasks.router)