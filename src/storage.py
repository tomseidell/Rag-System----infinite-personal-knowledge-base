from fastapi import HTTPException
from google.cloud import storage
from src.config import settings

def get_storage_client():
    return storage.Client()


def get_bucket():
    client = get_storage_client()
    return client.bucket(settings.GCS_BUCKET_NAME)



class StorageService:
    def __init__(self):
        self.bucket = get_bucket()

    def upload_doc(self, content:bytes, filename:str, user_id:int, content_type:str) ->str:
        try:
            bucket = get_bucket() # initialize connection to storage 
            blob_name = f"user_{user_id}/{filename}" # user specific name in storage
            blob = bucket.blob(blob_name) #create blob reference
            blob.upload_from_string(content, content_type=content_type) # save blob with given content to bucket 
        except:
            raise HTTPException(
                status_code=500,
                detail="Internal Server error"
            )
        return blob_name