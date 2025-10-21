from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import session
from sqlalchemy.orm.session import Session

from user.dependencies import get_user_service
from user.schemas import UserRegistration, UserRegistrationResponse
from user.service import UserService


router = APIRouter()

@router.post("/register", status_code=201, response_model=UserRegistrationResponse)
async def register(user:UserRegistration, user_service:UserService = Depends(get_user_service)):
    return user_service.create_user(user)
