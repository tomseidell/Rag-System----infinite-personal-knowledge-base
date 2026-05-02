import logging

import aioboto3
from botocore.exceptions import ClientError

from shared.config import settings
from api.clients.storage.exceptions import StorageException
from shared.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class AsyncStorageService:
    def __init__(self):
        self._session = aioboto3.Session()
        self.bucket_name = settings.S3_BUCKET_NAME
        self._endpoint_url = settings.S3_ENDPOINT_URL

    async def upload_file(self, content: bytes, filename: str, user_id: int) -> str:
        try:
            blob_name = f"user_{user_id}/{filename}" # allows to distinguish ressources between users
            async with self._session.client("s3", endpoint_url=self._endpoint_url) as s3:  # type: ignore[attr-defined]
                await s3.put_object(Bucket=self.bucket_name, Key=blob_name, Body=content)
            return blob_name
        except Exception as e:
            logger.critical(f"Failed to upload file to storage: {e}", exc_info=True)
            raise StorageException(operation="upload_file") from e

    async def get_file(self, storage_path: str) -> bytes:
        try:
            async with self._session.client("s3", endpoint_url=self._endpoint_url) as s3:  # type: ignore[attr-defined]
                response = await s3.get_object(Bucket=self.bucket_name, Key=storage_path)
                return await response["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.warning(f"File not found in S3 (NoSuchKey): {storage_path}")
                raise NotFoundException(ressource=f"File: {storage_path}") from e
            logger.critical(f"S3 error getting file: {e}", exc_info=True)
            raise StorageException(operation="get_file") from e
        except Exception as e:
            logger.critical(f"Unexpected error getting file: {e}", exc_info=True)
            raise StorageException(operation="get_file") from e

    async def delete_file(self, storage_path: str) -> None:
        try:
            async with self._session.client("s3", endpoint_url=self._endpoint_url) as s3:  # type: ignore[attr-defined]
                await s3.delete_object(Bucket=self.bucket_name, Key=storage_path)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.warning(f"File not found in S3 (NoSuchKey): {storage_path}")
                raise NotFoundException(ressource=f"File: {storage_path}") from e
            logger.critical(f"S3 error deleting file: {e}", exc_info=True)
            raise StorageException(operation="delete_file") from e
        except Exception as e:
            logger.critical(f"Unexpected error deleting file: {e}", exc_info=True)
            raise StorageException(operation="delete_file") from e
