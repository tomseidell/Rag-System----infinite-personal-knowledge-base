from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession  # ← AsyncSession!
from database import get_db
from user.repository import UserRepository
from user.service import UserService


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
     return UserRepository(db)

def get_user_service(repo: UserRepository = Depends(get_user_repository)):
    return UserService(repo) 
