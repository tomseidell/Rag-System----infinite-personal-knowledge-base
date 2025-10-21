from sqlalchemy.orm.session import Session
from src.user.model import User
from src.user.schemas import UserRegistration, UserRegistrationResponse
from src.user.utils import hash_password



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







def login_user():
    ""