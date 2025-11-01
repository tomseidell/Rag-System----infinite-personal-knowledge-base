from fastapi import Depends, HTTPException
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession  # ← AsyncSession!
from sqlalchemy import select  # ← select statt query!
from src.user.model import User
from src.user.schemas import UserLogin, UserRegistration
from src.user.utils import hash_password, verify_password
from user.dependencies import get_user_repository
from user.repository import UserRepository



class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository


    async def create_user(self, user: UserRegistration) -> User: 
        existing_user = await self.get_user(user.email)
        if existing_user:
            raise HTTPException(status_code=409, detail= "Email already registered")

        hashed_password = hash_password(user.password)
        return await self.user_repository.create_user(full_name=user.fullname, email=user.email, hashed_password=hashed_password)


    async def get_user(self, email:EmailStr) -> User:
        user = await self.user_repository.get_user_by_mail(email)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="No user registered with given mail"
        )
        

        return user


    async def login_user(self, user:UserLogin) -> User:
        db_user = await self.get_user(user.email)

        is_valid = verify_password(user.password, db_user.hashed_password)

        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid password"
        )
        await self.user_repository.update_last_login(db_user.id)
        
        return db_user
        


