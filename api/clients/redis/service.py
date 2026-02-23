from redis.exceptions import RedisError
import redis.asyncio as redis
import os  
from api.clients.redis.exceptions import RedisException
import logging

logger = logging.getLogger(__name__)


class RedisService:
    def __init__(self):
        self.client = redis.Redis.from_url(url=os.getenv("REDIS_URL", "http://localhost:6379"))

    async def _execute(self, operation: str, call):
        try:
            return await call
        except RedisError as e:
            logger.error(f"Redis error: in {operation}: {e}")
            raise RedisException(operation=operation)



    async def get(self, key: str):
        return await self._execute("get", self.client.get(key))

    async def set(self, key: str, value: str, ttl=None):
        await self._execute("set", self.client.set(key, value, ex=ttl))

    async def delete(self, key: str):
        await self._execute("delete", self.client.delete(key))

    async def incr(self, key: str) -> int:
        return await self._execute("incr", self.client.incr(key))

    async def expire(self, key: str, seconds: int):
        await self._execute("expire", self.client.expire(name=key, time=seconds))
