from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession  # ← AsyncSession!
from document.model import Document
from document.repository import DocumentRepository
from document.service import DocumentService
from src.database import get_db

from fastapi import Depends



def get_document_repository(db: AsyncSession = Depends(get_db)) -> DocumentRepository:
     return DocumentRepository(db)

def get_document_service(repo: DocumentRepository = Depends(get_document_repository)):
    return DocumentService(repo) 
