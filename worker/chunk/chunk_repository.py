from sqlalchemy.orm import Session

from shared.modules.chunk.model import Chunk


class ChunkRepositorySync:
    def __init__(self, db: Session):
        self.db = db

    def flush_many(self, chunks: list[Chunk]) -> list[Chunk]:
        self.db.add_all(chunks)
        self.db.flush()
        return chunks
