from src.clients.qdrant.service import AsyncQdrantService
from functools import lru_cache


@lru_cache() # because we do not have any dependencies we can create 1 instance as singleton
def get_qdrant_service() -> AsyncQdrantService:
    return AsyncQdrantService()