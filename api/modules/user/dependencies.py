from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession  # ← AsyncSession!
from shared.database import get_db
from api.modules.user.repository import UserRepository
from api.modules.user.service import UserService
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.modules.user.utils import decode_access_token


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
     return UserRepository(db)

def get_user_service(repo: UserRepository = Depends(get_user_repository)):
    return UserService(repo) 



security = HTTPBearer() # returns scheme and credentials

# dynamic, uncached function
async def get_current_user_id(credentials:HTTPAuthorizationCredentials = Depends(security)) -> int:
     """Extracts and validates jwt from request and returns user id """
     token = credentials.credentials
     user_id = decode_access_token(token) # throws error if token is invalid
     return user_id