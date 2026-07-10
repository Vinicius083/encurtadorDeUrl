import json

from app.db.redis import get_redis_client


class CacheService:
    def __init__(self):
        self.client = get_redis_client()

    def get(self, key: str) -> dict | None:
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return None

    def set(self, key: str, value: dict, ttl_seconds: int | None = None) -> None:
        data = json.dumps(value)
        self.client.set(key, data, ex=ttl_seconds)

    def delete(self, key: str) -> None:
        self.client.delete(key)

    def exists(self, key: str) -> bool:
        return self.client.exists(key) > 0
