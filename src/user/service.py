from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy.orm.session import Session
from src.user.model import User
from src.user.schemas import UserLogin, UserRegistration
from src.user.utils import hash_password, verify_passowrd



class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserRegistration) -> User: 
        hashed_password = hash_password(user.password)
        db_user = User(
            full_name = user.fullname,
            email = user.email,
            hashed_password = hashed_password 
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    def get_user(self, email:EmailStr)-> User:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="no user with this mail"
        )

        return user

    def login_user(self, user:UserLogin) -> User:
        db_user = self.get_user(user.email)

        if not db_user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
        )

        is_valid = verify_passowrd(user.password, db_user.hashed_password)

        return db_user
