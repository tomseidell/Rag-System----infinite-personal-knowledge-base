from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from shared.modules.document.model import Document
from sqlalchemy import select, delete
from shared.core.exceptions import DatabaseException, NotFoundException
from api.modules.document.exceptions import DocumentNotFoundException, DocumentAlreadyExistsException
from api.modules.document.schemas import DocumentCreate, GetDocuments


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document(self, data:DocumentCreate) -> Document:
        db_document = Document(**data.model_dump())
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
        
    async def get_document(self, user_id:int, document_id:int) -> Document | None:
        try:
            stmt = select(Document).where(Document.id == document_id, Document.user_id == user_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseException(
                operation="get_document",
                detail=str(e)
            ) 
        
    async def delete_document(self, user_id:int, document_id:int) -> Document | None:
        try:
            document = await self.get_document(user_id=user_id, document_id=document_id)

            if not document:
                raise DocumentNotFoundException(identifier=str(document_id))
            if document:
                stmt = delete(Document).where(Document.id == document_id, Document.user_id == user_id)
                await self.db.execute(stmt)
            return document
        


        except SQLAlchemyError as e:
            raise DatabaseException(
                operation="delete_document",
                detail=str(e)
            ) 
        
    async def get_documents(self, user_id: int,cursor: int | None = None,limit: int = 20) -> tuple[list[Document], int | None]:
        try:
            stmt = (
                select(Document)
                .where(Document.user_id == user_id)
                .order_by(Document.id.desc())
            )
            
            if cursor:
                stmt = stmt.where(Document.id < cursor) # smaller => more in the past 
            
            stmt = stmt.limit(limit + 1)  # fetch one extra for infinite fetch 
            
            result = await self.db.execute(stmt)
            documents = list(result.scalars().all()) # convert to list to ensure type safety 
            
            has_more = len(documents) > limit
            if has_more:
                documents = documents[:limit]  # Remove extra
                next_cursor = documents[-1].id  # Last doc ID
            else:
                next_cursor = None
            
            return documents, next_cursor
            
        except SQLAlchemyError as e:
            raise DatabaseException(
                operation="get_documents",
                detail=str(e)
            )

