from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from user.model import User
from sqlalchemy import select  


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
