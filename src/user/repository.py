from datetime import datetime
from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from src.user.model import User
from sqlalchemy import select, update  


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, full_name:str, email:EmailStr, hashed_password:str)-> User:
        db_user = User(
            full_name = full_name,
            email = email,
            hashed_password = hashed_password 
        )

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)

        return db_user


    async def get_user_by_mail(self, email:EmailStr) -> User:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        return user

    async def get_user_by_id(self, id:int) -> User:
        stmt = select(User).where(User.id == id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        return user


    async def update_last_login(self, id:int) -> None:
        stmt = update(User).where(User.id == id).values(
            last_login = datetime.now()
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def update_refresh_token(self, id:int, token:str) -> None:
        stmt = update(User).where(User.id == id).values(
            refresh_token=token
        )
        await self.db.execute(stmt)
        await self.db.commit()