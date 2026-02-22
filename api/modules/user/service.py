from re import S
from fastapi import Depends, HTTPException
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession  # ← AsyncSession!
from sqlalchemy import select  # ← select statt query!
from shared.modules.user.model import User
from api.modules.user.schemas import TokenResponse, UserLogin, UserRegistration
from api.modules.user.utils import create_access_token, create_refresh_token, hash_password, verify_password, decode_refresh_token
from api.modules.user.repository import UserRepository
from api.modules.user.exceptions import UserNotFoundException, InvalidTokenException



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
            "expires_in": 1800,
            "user": {
                "id": db_user.id,
                "email": db_user.email,
                "full_name": db_user.full_name
            }
        }
        

    async def update_refresh_token(self, id:int, refresh_token:str) ->None:
        await self.user_repository.update_refresh_token(id, refresh_token)


    async def handle_refresh(self, refresh_token:str):
        user_id = decode_refresh_token(refresh_token)
        db_user = await self.user_repository.get_user_by_id(id=user_id)
        if not db_user:
            raise UserNotFoundException(user_id)

        if db_user.refresh_token != refresh_token:
            raise InvalidTokenException()
        
        new_access_token = create_access_token(user_id)

        new_refresh_token = create_refresh_token(user_id)

        await self.update_refresh_token(user_id, new_refresh_token)

        return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token, expires_in=1800) 
