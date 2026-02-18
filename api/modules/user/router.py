from fastapi import APIRouter, Depends, HTTPException

from api.modules.user.dependencies import get_user_service
from api.modules.user.schemas import TokenResponse, UserLogin, UserRegistration, UserResponse, RefreshRequest
from api.modules.user.service import UserService
from api.modules.user.utils import create_access_token, create_refresh_token, decode_refresh_token


router = APIRouter()

@router.post("/register", status_code=201, response_model=UserResponse)
async def register(user:UserRegistration, user_service:UserService = Depends(get_user_service)):
    return await user_service.create_user(user)


@router.post("/login", status_code=200, response_model=TokenResponse)
async def login(user:UserLogin, user_service:UserService = Depends(get_user_service)):
    return await user_service.login_user(user)

@router.post("/refresh", status_code=200, response_model=TokenResponse)
async def refresh(refresh_request:RefreshRequest, user_service:UserService = Depends(get_user_service)):
    refresh_token = refresh_request.refresh_token
    return await user_service.handle_refresh(refresh_token=refresh_token)
