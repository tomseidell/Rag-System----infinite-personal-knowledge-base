from datetime import datetime
from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from document.model import Document
from user.model import User
from sqlalchemy import select, update  


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

async def create_document(
    self, 
    user_id: int,
    title: str,
    original_filename: str,
    storage_path: str,
    file_size: int,
    file_type: str,
    source_type: str,
    content_hash: str,
    source_id: str | None = None,
    chunk_count: int = 0
) -> Document:
    db_document = Document(
        user_id=user_id,
        title=title,
        original_filename=original_filename,
        storage_path=storage_path,
        file_size=file_size,
        file_type=file_type,
        source_type=source_type,
        content_hash=content_hash,
        source_id=source_id,
        chunk_count=chunk_count
    )
    
    self.db.add(db_document)
    await self.db.commit()
    await self.db.refresh(db_document)
    
    return db_document
