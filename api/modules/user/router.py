from fastapi import APIRouter, Depends, HTTPException, Request, Response
from typing import Annotated

from shared.config import settings
from api.modules.user.dependencies import get_user_service
from api.modules.user.schemas import UserLogin, UserRegistration, UserResponse
from api.modules.user.service import UserService


router = APIRouter()

UserServiceDep = Annotated[UserService, Depends(get_user_service)]

_COOKIE_SECURE = settings.ENVIRONMENT == "production"


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie( # send via response header
        key="access_token",
        value=access_token,
        httponly=True, # only allow browser to read cookie
        secure=_COOKIE_SECURE, # send cookie trough https 
        samesite="strict", # forbid other pages to send cookie
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, 
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=_COOKIE_SECURE,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/register", status_code=201, response_model=UserResponse)
async def register(user: UserRegistration, user_service: UserServiceDep):
    return await user_service.create_user(user)


@router.post("/login", status_code=200)
async def login(user_login: UserLogin, user_service: UserServiceDep, response: Response):
    tokens = await user_service.login_user(user_login)
    _set_auth_cookies(response, tokens.access_token, tokens.refresh_token) # send cookie via 
    return {"message": "Login successful"}


@router.post("/refresh", status_code=200)
async def refresh(request: Request, user_service: UserServiceDep, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    tokens = await user_service.handle_refresh(refresh_token=refresh_token)
    _set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return {"message": "Token refreshed"}


@router.post("/logout", status_code=200)
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}
