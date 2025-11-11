from google.cloud import storage
from src.config import settings

def get_storage_client():
    return storage.Client()


def get_bucket():
    client = get_storage_client()
    return client.bucket(settings.GCS_BUCKET_NAME)