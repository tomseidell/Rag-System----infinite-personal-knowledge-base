from datetime import datetime
from pydantic import EmailStr
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import DatabaseException
from app.modules.user.model import User
from sqlalchemy import select, update  


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, full_name:str, email:EmailStr, hashed_password:str)-> User:
        try:
            db_user = User(
                full_name = full_name,
                email = email,
                hashed_password = hashed_password 
            )
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
            return db_user
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseException(
                operation="create_user",
                detail= str(e)
            )


    async def get_user_by_mail(self, email:EmailStr) -> User | None:
        try:
            stmt = select(User).where(User.email == email)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            return user
        except SQLAlchemyError as e:
            raise DatabaseException(
                operation="get_user_by_mail",
                detail = str(e)
            )


    async def get_user_by_id(self, id:int) -> User | None:
        try: 
            stmt = select(User).where(User.id == id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            return user
        except SQLAlchemyError as e:
            raise DatabaseException(
                operation="get_user_by_id",
                detail = str(e)
            )


    async def update_last_login(self, id:int) -> None:
        try:
            stmt = update(User).where(User.id == id).values(
                last_login = datetime.now()
            )
            await self.db.execute(stmt)
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseException(
                operation="update_last_login",
                detail=str(e)
            )

    async def update_refresh_token(self, id:int, token:str) -> None:
        try:
            stmt = update(User).where(User.id == id).values(
                refresh_token=token
            )
            await self.db.execute(stmt)
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseException(
                operation="update_refresh_token",
                detail = str(e)
            ) 