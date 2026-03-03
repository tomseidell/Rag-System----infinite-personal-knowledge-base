from sqlalchemy.ext.asyncio import AsyncSession
from shared.modules.chunk.model import Chunk
from sqlalchemy.exc import SQLAlchemyError
from shared.core.exceptions import DatabaseException
from sqlalchemy import select, delete


class ChunkRepository:
    def __init__(self, db:AsyncSession):
        self.db= db
    
    async def get_chunks_for_doc(self, user_id:int, document_id:int) -> list[Chunk]:
        try:
            stmt = select(Chunk).where(Chunk.user_id == user_id, Chunk.document_id == document_id)
            result = await self.db.execute(stmt)
            chunks = list(result.scalars().all())
            return chunks
        except SQLAlchemyError as e:
            raise DatabaseException(
                operation="get chunks for document",
                detail= str(e)
            )
    
    async def delete_chunks_for_doc(self, user_id:int, document_id:int) -> None:
        try:
            stmt = delete(Chunk).where(Chunk.user_id == user_id, Chunk.document_id == document_id)
            await self.db.execute(stmt)
        except SQLAlchemyError as e:
            raise DatabaseException(
                operation="delete chunks for document",
                detail=str(e)
            )