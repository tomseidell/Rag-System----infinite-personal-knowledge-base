from shared.modules.chunk.model import Chunk

from worker.repositories.chunk_repository import ChunkRepositorySync


class ChunkServiceSync:
    def __init__(self, repo: ChunkRepositorySync):
        self.repo = repo

    def create_chunks_from_text(
        self, chunks: list[str], document_id: int, user_id: int
    ) -> list[Chunk]:
        chunk_objects = [
            Chunk(
                text=chunk,
                document_id=document_id,
                chunk_index=i,
                user_id=user_id,
            )
            for i, chunk in enumerate(chunks, start=1)
        ]
        return self.repo.flush_many(chunks=chunk_objects)
