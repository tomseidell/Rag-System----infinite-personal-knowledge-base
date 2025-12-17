from fastapi import HTTPException
from google.cloud import storage
from src.config import settings
import logging
from src.clients.storage.exceptions import StorageException
from google.cloud.exceptions import GoogleCloudError, NotFound
from src.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


def get_storage_client():
    return storage.Client()


def get_bucket():
    client = get_storage_client()
    return client.bucket(settings.GCS_BUCKET_NAME)


class StorageService:
    def __init__(self):
        try:
            self.bucket = get_bucket()
            logger.info("Storage service initialized")
        except Exception as e:
            logger.critical(f"Failed to initialize storage: {e}", exc_info=True)
            raise StorageException(operation="Initializing Storage") 



    def upload_file(self, content:bytes, filename:str, user_id:int, content_type:str) ->str:
        try:
            blob_name = f"user_{user_id}/{filename}" # user specific name in storage
            blob = self.bucket.blob(blob_name) #create blob reference
            blob.upload_from_string(content, content_type=content_type) # save blob with given content to bucket 
            return blob_name
        except GoogleCloudError as e:
            logger.error(f"Google Cloud failed to upload file {e}", exc_info=True)
            raise StorageException(operation="upload_file") from e
        except Exception as e:
            logger.critical(f"Failed to upload file to storage: {e}", exc_info=True)
            raise StorageException(operation="upload_file") from e 
        
    def get_file(self, storage_path:str) -> bytes:
        try:
            blob = self.bucket.blob(storage_path)
            return blob.download_as_bytes()
        except NotFound as e:
            logger.error(f"Could not find file: {storage_path}", exc_info=True)
            raise NotFoundException(ressource=f"File: {storage_path}") from e
        except GoogleCloudError as e:
            logger.error(f"Google Cloud failed to load file: {storage_path}", exc_info=True)
            raise StorageException(operation="get_file") from e
        except Exception as e:
            logger.critical(f"Failed to get file from storage: {e}", exc_info=True)
            raise StorageException(operation="get_file") from e 

    def delete_file(self, storage_path:str) -> None:
        try:
            blob = self.bucket.blob(storage_path)
            if blob.exists():
                blob.delete()
        except NotFound as e:
            logger.error(f"Could not find file: {storage_path}", exc_info=True)
            raise NotFoundException(ressource=f"File: {storage_path}") from e
        except GoogleCloudError as e:
            logger.error(f"Google Cloud failed to delete file: {storage_path}", exc_info=True)
            raise StorageException(operation="delete_file") from e
        except Exception as e:
            logger.critical(f"Failed to delete file from storage: {e}", exc_info=True)
            raise StorageException(operation="delete_file") from e 

    def file_exists(self, storage_path:str) ->bool:
        blob = self.bucket.blob(storage_path)
        return blob.exists()