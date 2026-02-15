from shared.modules.chunk.model import Chunk
from api.modules.chunk.repository import ChunkRepository
from qdrant_client.models import ExtendedPointId


class ChunkServiceAsync():
    def __init__(self, repositoy: ChunkRepository):
        self.repository = repositoy

    async def get_chunks_for_doc(self, document_id:int, user_id:int)->list[ExtendedPointId]:
        result = await self.repository.get_chunks_for_doc(document_id=document_id, user_id=user_id)
        chunk_ids: list[ExtendedPointId] = [chunk.id for chunk in result]
        return chunk_ids
    
    async def delete_chunks_for_doc(self, document_id:int, user_id:int):
        result = await self.repository.delete_chunks_for_doc(document_id=document_id, user_id=user_id)

