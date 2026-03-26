import redis
from core.config import get_settings

settings = get_settings()

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True,
)


# ==========================================================
# Health Check
# ==========================================================
def check_redis_connection():
    try:
        redis_client.ping()
    except Exception:
        raise RuntimeError("Redis is not available")


# ==========================================================
# Keys
# ==========================================================

def rate_limit_key(identifier: str) -> str:
    return f"rl:v1:{identifier}"


def token_blacklist_key(jti: str) -> str:
    return f"bl:v1:{jti}"


def session_key(user_id: int) -> str:
    return f"session:v1:{user_id}"