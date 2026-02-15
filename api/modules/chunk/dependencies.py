from sqlalchemy.ext.asyncio import AsyncSession  # ← AsyncSession!
from app.database import get_db
from fastapi import Depends
from app.modules.chunk.repository import ChunkRepository
from app.modules.chunk.service import ChunkServiceAsync


def get_chunk_repository(db: AsyncSession = Depends(get_db)):
    return ChunkRepository(db=db)

def get_chunk_service_async(repository:ChunkRepository = Depends(get_chunk_repository)):
    return ChunkServiceAsync(repositoy=repository)