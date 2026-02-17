from api.clients.storage.service import AsyncStorageService
from functools import lru_cache


@lru_cache() # because we do not have any dependencies we can create 1 instance as singleton
def get_storage_service() -> AsyncStorageService:
    return AsyncStorageService()