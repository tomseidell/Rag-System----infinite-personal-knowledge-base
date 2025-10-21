from fastapi import APIRouter, Depends

from user.dependencies import get_user_service
from user.schemas import UserLogin, UserRegistration, UserResponse
from user.service import UserService


router = APIRouter()

@router.post("/register", status_code=201, response_model=UserResponse)
async def register(user:UserRegistration, user_service:UserService = Depends(get_user_service)):
    return await user_service.create_user(user)


@router.post("/login", status_code=200, response_model=UserResponse)
async def login(user:UserLogin, user_service:UserService = Depends(get_user_service)):
    return await user_service.login_user(user)