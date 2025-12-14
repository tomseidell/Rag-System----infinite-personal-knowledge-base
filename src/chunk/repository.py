from sqlalchemy.ext.asyncio import AsyncSession
from src.chunk.model import Chunk
from sqlalchemy.exc import SQLAlchemyError
from src.core.exceptions import DatabaseException
from src.chunk.schemas import ChunkCreate
from sqlalchemy import select
from sqlalchemy.orm import Session
import logging


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
        
class SyncChunkRepository:
    def __init__(self, db : Session):
        self.db = db

    def create_chunk(self, chunk:ChunkCreate) -> Chunk:
        try:
            chunk_obj = Chunk(
                text = chunk.text,
                document_id = chunk.document_id,
                user_id = chunk.user_id,
                chunk_index = chunk.chunk_index,
            )
            self.db.add(chunk_obj)
            self.db.flush()
            return chunk_obj
        except SQLAlchemyError as e:
            self.db.rollback() 
            logging.error(f"DB Error in create_chunk: {e}") 
            raise DatabaseException(
                operation="create_chunk",
                detail= str(e)
            )
        