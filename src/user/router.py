from fastapi import APIRouter, Depends

from user.dependencies import get_user_service
from user.schemas import UserRegistration, UserResponse
from user.service import UserService


router = APIRouter()

@router.post("/register", status_code=201, response_model=UserResponse)
async def register(user:UserRegistration, user_service:UserService = Depends(get_user_service)):
    return await user_service.create_user(user)
