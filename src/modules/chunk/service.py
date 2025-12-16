from src.modules.chunk.model import Chunk
from src.modules.chunk.repository import ChunkRepositorySync

class ChunkServiceSync():

    def __init__(self, repo :ChunkRepositorySync):
        self.repo = repo

    def create_chunks_from_text(self,chunks:list[str], document_id:int, user_id:int):
        chunk_objects=[]
        for i, chunk in enumerate(chunks, start=1): 
            chunk_objects.append(Chunk(
                id=f"{document_id}_{i}",
                text=chunk,
                document_id=document_id,
                chunk_index=i,
                user_id=user_id  
            ))

        return self.repo.flush_many(chunks=chunk_objects)