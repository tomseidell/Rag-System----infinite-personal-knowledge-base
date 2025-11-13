from datetime import datetime
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from src.document.model import Document
from sqlalchemy import select, update
from src.core.exceptions import DatabaseException  


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
        try:
            self.db.add(db_document)
            await self.db.commit()
            await self.db.refresh(db_document)
            return db_document
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseException(
                operation="create_document",
                detail=str(e)
            )

    
    async def check_for_existing_hash(self, content_hash:str, user_id:int) -> Document | None:
        try:
            stmt = select(Document).where(Document.content_hash == content_hash, Document.user_id==user_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none() 
        except SQLAlchemyError as e:
            raise DatabaseException(
                operation="check_for_existing_hash",
                detail=str(e)
            ) 