from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession  # ← AsyncSession!
from api.modules.document.repository import DocumentRepository
from api.modules.user.repository import UserRepository
from api.modules.document.service import DocumentService
from shared.database import get_db

from fastapi import Depends

from api.clients.storage.service import StorageService
from api.clients.storage.dependencies import get_storage_service

from api.clients.qdrant.service import AsyncQdrantService
from api.clients.qdrant.dependencies import get_qdrant_service

from api.modules.user.dependencies import get_user_repository

from api.modules.chunk.service import ChunkServiceAsync
from api.modules.chunk.dependencies import get_chunk_service_async



def get_document_repository(db: AsyncSession = Depends(get_db)) -> DocumentRepository:
     return DocumentRepository(db)

def get_document_service(
     document_repo: DocumentRepository = Depends(get_document_repository),
     storage:StorageService = Depends(get_storage_service),
     user_repo:UserRepository = Depends(get_user_repository),
     qdrant_service:AsyncQdrantService = Depends(get_qdrant_service),
     chunk_service:ChunkServiceAsync = Depends(get_chunk_service_async),
     db: AsyncSession = Depends(get_db)
     ):
    return DocumentService(document_repository=document_repo, storage=storage,user_repository=user_repo, qdrant_service=qdrant_service, chunk_service=chunk_service, db=db) 
