from api.clients.redis.service import RedisService
from functools import lru_cache


@lru_cache() # because we do not have any dependencies we can create 1 instance as singleton
def get_redis_service() -> RedisService:
    return RedisService()