from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession  # ← AsyncSession!
from sqlalchemy import select  # ← select statt query!
from src.user.model import User
from src.user.schemas import UserLogin, UserRegistration
from src.user.utils import hash_password, verify_password



class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user: UserRegistration) -> User: 
        hashed_password = hash_password(user.password)
        db_user = User(
            full_name = user.fullname,
            email = user.email,
            hashed_password = hashed_password 
        )

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)

        return db_user

    async def get_user(self, email:EmailStr)-> User:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="no user with this mail"
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
        
        return db_user
        



