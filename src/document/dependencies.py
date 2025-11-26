from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession  # ← AsyncSession!
from src.document.repository import DocumentRepository
from src.user.repository import UserRepository
from src.document.service import DocumentService
from src.database import get_db

from fastapi import Depends

from storage.service import StorageService
from src.storage.dependencies import get_storage_service
from src.user.dependencies import get_user_repository



def get_document_repository(db: AsyncSession = Depends(get_db)) -> DocumentRepository:
     return DocumentRepository(db)

def get_document_service(repo: DocumentRepository = Depends(get_document_repository), storage:StorageService = Depends(get_storage_service), user_repo:UserRepository = Depends(get_user_repository)):
    return DocumentService(repo, storage,user_repo) 
