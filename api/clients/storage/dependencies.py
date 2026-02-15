from app.clients.storage.service import StorageService
from functools import lru_cache


@lru_cache() # because we do not have any dependencies we can create 1 instance as singleton
def get_storage_service() -> StorageService:
    return StorageService()