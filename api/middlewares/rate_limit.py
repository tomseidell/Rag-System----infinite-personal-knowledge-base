from fastapi import Request
from api.clients.redis.dependency import get_redis_service
from fastapi.responses import JSONResponse

async def rate_limit_middleware(request: Request, call_next): # call next gets automatically handled by fast api
    redis_service = get_redis_service() # get singleton redis instance 

    if request.url.path in ["/health", "/metrics"]: # allow prometheus and health checks 
        return await call_next(request) # go to next middleware
    
    if not request.client: # decline request without client information (needed for ip checking)
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid http request"}
        )

    client_ip = request.client.host
 
    key = f"ratelimit:{client_ip}"
    
    # creates new key, or increments existing 
    count: int = await redis_service.incr(key)
    if count == 1: # created new key
        await redis_service.expire(key, 60) # delete key after 60 seconds
    
    if count > 100: # 100 requests per second
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests, try again later."}
        )
    
    return await call_next(request)


