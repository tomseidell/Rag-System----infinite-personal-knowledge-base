import redis.asyncio as redis
import os  

class RedisService:
    def __init__(self):
        self.client = redis.Redis.from_url(url=os.getenv("REDIS_URL","http://localhost:6379"))

    async def get(self, key: str):
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, ttl=None): # ttl = time to live in cache 
        await self.client.set(key, value, ex=ttl)
    
    async def delete(self, key: str):
        await self.client.delete(key)

    async def incr(self, key: str) -> int: # creates key with 0 and increments
        result = await self.client.incr(key)
        return result  

    async def expire(self, key:str, seconds:int):
        await self.client.expire(name=key, time=seconds)