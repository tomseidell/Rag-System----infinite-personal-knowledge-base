from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import session
from sqlalchemy.orm.session import Session

from database import get_db
from user.service import create_user
from .schemas import UserRegistration, UserRegistrationResponse
from .utils import hash_password
from .model import User

router = APIRouter()

@router.post("/register", status_code=201, response_model=UserRegistrationResponse)
async def register(user:UserRegistration,db: Session = Depends(get_db)):
    return create_user(user, db)




    return {
        "id": 1,
        "email": user.email,
        "fullname": user.fullname,
        "is_active": True,
        "created_at": datetime.now()
    }