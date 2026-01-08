from fastapi import Request
from src.clients.redis.dependency import get_redis_service
from fastapi.responses import JSONResponse

async def rate_limit_middleware(request: Request, call_next): # call next gets automatically handled by fast api
    redis_service = get_redis_service() # get singleton redis instance 

    if request.url.path in ["/health", "/metrics"]: # allow prometheus and health checks 
        return await call_next(request) # go to next middleware
    
    if not request.client: # decline request without request client 
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid http request"}
        )

    client_ip = request.client.host
 
    key = f"ratelimit:{client_ip}"
    
    count: int = await redis_service.incr(key)
    if count == 1:
        await redis_service.expire(key, 60)
    
    if count > 100:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests, try again later."}
        )
    
    return await call_next(request)


