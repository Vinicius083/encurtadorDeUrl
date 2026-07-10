import redis

from app.core.config import get_settings

_redis_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    settings = get_settings()
    pool = redis.ConnectionPool(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password or None,
        decode_responses=True,
    )
    _redis_client = redis.Redis(connection_pool=pool)
    return _redis_client


def close_redis() -> None:
    global _redis_client

    if _redis_client is not None:
        _redis_client.close()
        _redis_client = None
