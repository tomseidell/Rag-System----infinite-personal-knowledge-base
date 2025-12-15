import bcrypt
from datetime import datetime, timedelta, timezone 
from fastapi import HTTPException
import jwt
from src.config import settings



def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Convert string to bytes
    password_bytes = password.encode('utf-8')
    
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    # Convert to bytes
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    
    # Verify
    return bcrypt.checkpw(password_bytes, hashed_bytes)



# jwt 
def create_access_token(user_id:int) -> str:
    """creates jwt access token based on userId"""

    expire = datetime.now(timezone.utc) + timedelta(minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "user_id":user_id,
        "exp": expire,
        "type":"access"
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)

    return token 


def create_refresh_token(user_id:int) -> str:
    """creates jwt access token based on userId"""
    expire = datetime.now(timezone.utc) + timedelta(minutes = settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    payload = {
        "user_id":user_id,
        "exp": expire,
        "type":"refresh"
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)

    return token 


def decode_access_token(token:str) -> int:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(401, "wrong token type")
        return payload["user_id"] 
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def decode_refresh_token(token:str) ->int:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(401, "wrong token type")
        return payload["user_id"]
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

