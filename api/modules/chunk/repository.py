from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.chunk.model import Chunk
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import DatabaseException
from app.modules.chunk.schemas import ChunkCreate
from sqlalchemy import select, delete


class ChunkRepository:
    def __init__(self, db:AsyncSession):
        self.db= db


    async def create_chunk(self, chunk:ChunkCreate) ->Chunk:
        try:
            chunk = Chunk(
                text = chunk.text,
                document_id = chunk.document_id,
                user_id = chunk.user_id,
                chunk_index = chunk.chunk_index,
            )
            self.db.add(chunk)
            await self.db.commit()
            await self.db.refresh(chunk)
            return chunk
        except SQLAlchemyError as e:
            await self.db.rollback() 
            raise DatabaseException(
                operation="create_chunk",
                detail= str(e)
            )
        
    async def get_chunk(self, user_id:int, chunk_id:int) -> Chunk:
        try:
            stmt= select(Chunk).where(Chunk.user_id == user_id, Chunk.id==chunk_id)
            result = await self.db.execute(stmt)
            chunk = result.scalar_one_or_none()
            return chunk
        except SQLAlchemyError as e:
            raise DatabaseException(
                operation= "get chunk",
                detail = str(e)
            )

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
    
    async def delete_chunks_for_doc(self, user_id:int, document_id:int):
        try:
            stmt = delete(Chunk).where(Chunk.user_id == user_id, Chunk.document_id == document_id)
            await self.db.execute(stmt)
        except SQLAlchemyError as e:
            raise DatabaseException(
                operation="delete chunks for document",
                detail=str(e)
            )