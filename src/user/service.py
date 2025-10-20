from sqlalchemy.orm.session import Session
from user.model import User
from user.schemas import UserRegistration
from user.utils import hash_password


def create_user(user: UserRegistration, db:Session) : 
    hashed_password = hash_password(user.password)

    db_user = User(
        fullname = user.fullname,
        email = user.email,
        password = hashed_password 
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
