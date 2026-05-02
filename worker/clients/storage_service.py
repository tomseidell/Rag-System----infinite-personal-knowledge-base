import logging

import boto3
from botocore.exceptions import ClientError

from shared.config import settings
from shared.core.exceptions import NotFoundException, StorageException

logger = logging.getLogger(__name__)

__all__ = ["StorageService"]


class StorageService:
    def __init__(self):
        self._s3 = boto3.client("s3", endpoint_url=settings.S3_ENDPOINT_URL or None)
        self.bucket_name = settings.S3_BUCKET_NAME
        logger.info("Storage service initialized")

    def upload_file(self, content: bytes, filename: str, user_id: int, content_type: str) -> str:
        try:
            blob_name = f"user_{user_id}/{filename}"
            self._s3.put_object(
                Bucket=self.bucket_name,
                Key=blob_name,
                Body=content,
                ContentType=content_type,
            )
            return blob_name
        except Exception as e:
            logger.critical(f"Failed to upload file to storage: {e}", exc_info=True)
            raise StorageException(operation="upload_file") from e

    def get_file(self, storage_path: str) -> bytes:
        try:
            response = self._s3.get_object(Bucket=self.bucket_name, Key=storage_path)
            return response["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.error(f"Could not find file: {storage_path}", exc_info=True)
                raise NotFoundException(ressource=f"File: {storage_path}") from e
            logger.critical(f"S3 error getting file: {storage_path}", exc_info=True)
            raise StorageException(operation="get_file") from e
        except Exception as e:
            logger.critical(f"Failed to get file from storage: {e}", exc_info=True)
            raise StorageException(operation="get_file") from e

    def delete_file(self, storage_path: str) -> None:
        try:
            self._s3.delete_object(Bucket=self.bucket_name, Key=storage_path)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.error(f"Could not find file: {storage_path}", exc_info=True)
                raise NotFoundException(ressource=f"File: {storage_path}") from e
            logger.critical(f"S3 error deleting file: {storage_path}", exc_info=True)
            raise StorageException(operation="delete_file") from e
        except Exception as e:
            logger.critical(f"Failed to delete file from storage: {e}", exc_info=True)
            raise StorageException(operation="delete_file") from e

    def file_exists(self, storage_path: str) -> bool:
        try:
            self._s3.head_object(Bucket=self.bucket_name, Key=storage_path)
            return True
        except ClientError:
            return False
