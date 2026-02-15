from fastapi import APIRouter, Depends, HTTPException

from app.modules.user.dependencies import get_user_service
from app.modules.user.schemas import TokenResponse, UserLogin, UserRegistration, UserResponse
from app.modules.user.service import UserService
from app.modules.user.utils import create_access_token, create_refresh_token, decode_refresh_token


router = APIRouter()

@router.post("/register", status_code=201, response_model=UserResponse)
async def register(user:UserRegistration, user_service:UserService = Depends(get_user_service)):
    return await user_service.create_user(user)


@router.post("/login", status_code=200, response_model=TokenResponse)
async def login(user:UserLogin, user_service:UserService = Depends(get_user_service)):
    return await user_service.login_user(user)

@router.post("/refresh", status_code=200, response_model=TokenResponse)
async def refresh(refresh_token:str, user_service:UserService = Depends(get_user_service)):
    user_id = decode_refresh_token(refresh_token)

    db_user = await user_service.get_user_by_id(user_id)
    if db_user.refresh_token != refresh_token:
        raise HTTPException(401, "Invalid refresh token")
    
    new_access_token = create_access_token(user_id)

    new_refresh_token = create_refresh_token(user_id)

    await user_service.update_refresh_token(user_id, new_refresh_token)

    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token, expires_in=1800) # expires in in seconds