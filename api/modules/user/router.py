from fastapi import APIRouter, Depends
from typing import Annotated


from api.modules.user.dependencies import get_user_service
from api.modules.user.schemas import TokenResponse, UserLogin, UserRegistration, UserResponse, RefreshRequest
from api.modules.user.service import UserService


router = APIRouter()

# use annotated to share dependency
UserServiceDep = Annotated[UserService, Depends(get_user_service)]

@router.post("/register", status_code=201, response_model=UserResponse)
async def register(user:UserRegistration, user_service:UserServiceDep):
    return await user_service.create_user(user)


@router.post("/login", status_code=200, response_model=TokenResponse)
async def login(user_login:UserLogin, user_service:UserServiceDep):
    return await user_service.login_user(user_login)

@router.post("/refresh", status_code=200, response_model=TokenResponse)
async def refresh(refresh_request:RefreshRequest, user_service:UserServiceDep):
    refresh_token = refresh_request.refresh_token
    return await user_service.handle_refresh(refresh_token=refresh_token)
