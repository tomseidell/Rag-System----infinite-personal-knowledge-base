from fastapi import Depends
from sqlalchemy.orm.session import Session
from database import get_db
from user.service import UserService


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)  