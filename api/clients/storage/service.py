from shared.config import settings
import logging
from api.clients.storage.exceptions import StorageException
from shared.core.exceptions import NotFoundException

from gcloud.aio.storage import Storage

from aiohttp import ClientResponseError



logger = logging.getLogger(__name__)


class AsyncStorageService:
    def __init__(self):
        try:
            self.storage_client = Storage()
            self.bucket_name = (settings.GCS_BUCKET_NAME)
        except Exception as e:
            logger.critical(f"Failed to initialize storage {e}", exc_info=True)

    
    async def upload_file(self, content: bytes, filename: str, user_id: int, content_type:str) -> str:
        try:
            blob_name = f"user_{user_id}/{filename}"
            await self.storage_client.upload(object_name=blob_name, bucket=self.bucket_name, file_data=content)
            return blob_name
        except Exception as e:
            logger.critical(f"Failed to upload file to storage: {e}", exc_info=True)
            raise StorageException(operation="upload_file") from e


    async def get_file(self, storage_path:str) -> bytes:
        try:
            content = await self.storage_client.download(object_name=storage_path, bucket=self.bucket_name)
            return content ## return content as bytes
        except ClientResponseError as e:
            if e. status == 404:
                logger.warning(f"File not found in GCS (404): {storage_path}") # Nur eine Warnung, kein kritischer Fehler!
                raise NotFoundException(ressource=f"File: {storage_path}") from e
            else:
                logger.critical(f"Storage error: {e}", exc_info=True)
                raise StorageException(operation="get_file") from e 
        except Exception as e:
            logger.critical(f"Unexcepted error: {e}", exc_info=True)
            raise StorageException(operation="get_file") from e 
        

    async def delete_file(self, storage_path:str) -> None:
        try:
            await self.storage_client.delete(object_name=storage_path, bucket=self.bucket_name)
        except ClientResponseError as e:
            if e. status == 404:
                logger.warning(f"File not found in GCS (404): {storage_path}") # Nur eine Warnung, kein kritischer Fehler!
                raise NotFoundException(ressource=f"File: {storage_path}") from e
            else:
                logger.critical(f"Storage error: {e}", exc_info=True)
                raise StorageException(operation="delete_file") from e 
        except Exception as e:
            logger.critical(f"Unexcepted error: {e}", exc_info=True)
            raise StorageException(operation="delete_file") from e 