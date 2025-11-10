from re import S
from fastapi import Depends, HTTPException
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession  # ← AsyncSession!
from sqlalchemy import select  # ← select statt query!
from src.user.model import User
from src.user.schemas import UserLogin, UserRegistration
from src.user.utils import create_access_token, create_refresh_token, hash_password, verify_password
from user.dependencies import get_user_repository
from user.repository import UserRepository



class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository


    async def create_user(self, user: UserRegistration) -> User: 
        existing_user = await self.get_user_by_mail(user.email)
        if existing_user:
            raise HTTPException(status_code=409, detail= "Email already registered")

        hashed_password = hash_password(user.password)
        return await self.user_repository.create_user(full_name=user.fullname, email=user.email, hashed_password=hashed_password)


    async def get_user_by_mail(self, email:EmailStr) -> User:
        user = await self.user_repository.get_user_by_mail(email)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="No user registered with given mail"
        )
        

        return user

    async def get_user_by_id(self, id:int) -> User:
        user = await self.user_repository.get_user_by_id(id)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="No user registered with given mail"
        )
        return user


    async def login_user(self, user:UserLogin) -> dict:
        db_user = await self.get_user_by_mail(user.email)

        is_valid = verify_password(user.password, db_user.hashed_password)

        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid password"
        )
        await self.user_repository.update_last_login(db_user.id)

        access_token = create_access_token(db_user.id)
        refresh_token = create_refresh_token(db_user.id)

        await self.user_repository.update_refresh_token(db_user.id, refresh_token)
        
        return{
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": db_user.id,
                "email": db_user.email,
                "full_name": db_user.full_name
            }
        }
        

    async def update_refresh_token(self, id:int, refresh_token:str) ->None:

        await self.user_repository.update_refresh_token(id, refresh_token)

