from fastapi import APIRouter
from datetime import datetime

from fastapi import APIRouter
from datetime import datetime

from db.session import SessionLocal
from core.cache.redis_client import redis_client


router = APIRouter(tags=["HEALTH"])


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/ready")
def readiness_check():
    checks = {}

    # =========================
    # DB Check
    # =========================
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "fail"
    finally:
        db.close()

    # =========================
    # Redis Check
    # =========================
    try:
        redis_client.ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "fail"

    status = "ok" if all(v == "ok" for v in checks.values()) else "fail"

    return {
        "status": status,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }