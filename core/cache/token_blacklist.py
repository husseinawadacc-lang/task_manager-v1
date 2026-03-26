from core.cache.redis_client import redis_client
from core.cache.redis_client import token_blacklist_key


def blacklist_token(jti: str, ttl: int) -> None:
    redis_client.setex(
        token_blacklist_key(jti),
        ttl,
        "blacklisted"
    )


def is_token_blacklisted(jti: str) -> bool:
    return redis_client.exists(
        token_blacklist_key(jti)
    ) == 1
