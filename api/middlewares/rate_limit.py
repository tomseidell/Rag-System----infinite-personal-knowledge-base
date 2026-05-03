from fastapi import Request
from api.clients.redis.dependency import get_redis_service
from fastapi.responses import JSONResponse

AUTH_PATHS = {"/user/login", "/user/register"}
AUTH_LIMIT = 10
AUTH_TTL = 60 * 60 * 24  # 24 hours

async def rate_limit_middleware(request: Request, call_next):
    redis_service = get_redis_service()

    # skip rate limits for urls:
    if request.url.path in ["/health", "/metrics"]:
        return await call_next(request)

    if not request.client:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid http request"}
        )

    client_ip = request.client.host

    # custom rate limiting for login:
    if request.url.path in AUTH_PATHS:
        auth_key = f"ratelimit:auth:{client_ip}"
        count: int = await redis_service.incr(auth_key)
        if count == 1:
            await redis_service.expire(auth_key, AUTH_TTL)
        if count > AUTH_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many attempts, try again tomorrow."}
            )

    # global rate limitter
    key = f"ratelimit:{client_ip}"
    count: int = await redis_service.incr(key)
    if count == 1:
        await redis_service.expire(key, 60)
    if count > 100: # 100 requests per minute max
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests, try again later."}
        )

    return await call_next(request)


