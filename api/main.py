from fastapi import FastAPI
from api.v1.router import api_router
from api.exceptions import register_exception_handlers
app = FastAPI(title="task manger")

# =====================================================
# Exception handlers registration
# =====================================================
register_exception_handlers(app)
# =====================================================
# Routers
# =====================================================
app.include_router(api_router,prefix="/api/v1")
