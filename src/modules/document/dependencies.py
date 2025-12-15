from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession  # ← AsyncSession!
from src.modules.document.repository import DocumentRepository
from src.modules.user.repository import UserRepository
from src.modules.document.service import DocumentService
from src.database import get_db

from fastapi import Depends

from src.clients.storage.service import StorageService
from src.clients.storage.dependencies import get_storage_service
from src.modules.user.dependencies import get_user_repository



def get_document_repository(db: AsyncSession = Depends(get_db)) -> DocumentRepository:
     return DocumentRepository(db)

def get_document_service(repo: DocumentRepository = Depends(get_document_repository), storage:StorageService = Depends(get_storage_service), user_repo:UserRepository = Depends(get_user_repository)):
    return DocumentService(repo, storage,user_repo) 
