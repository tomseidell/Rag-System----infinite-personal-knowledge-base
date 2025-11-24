from fastapi import HTTPException, UploadFile
from src.document.model import Document
from src.document.repository import DocumentRepository
import hashlib
from src.document.schemas import DocumentCreate

from src.core.exceptions import InputError

from storage import get_bucket

class DocumentService:
    def __init__(self, document_repository:DocumentRepository):
        self.document_repository = document_repository


    async def upload_document(self, user_id: int, title: str| None, file:UploadFile,) -> Document:
        content = await file.read()

        if not file.filename:
            raise InputError(
                operation="upload_document",
                detail="Filename is missing"
            )
        
        content_type = file.content_type or "application/octet-stream" # fallback undefined content type
        content_hash = self._calculate_hash(content=content)

        existing = await self.document_repository.check_for_existing_hash(user_id=user_id, content_hash=content_hash)

        if existing: #do not save document if already existing 
            return existing 

        if not title: # if no title provided, create title automatically based on filename
            title = self._create_title_from_file(filename=file.filename)

        source_type = self._get_source_type_from_file(filename=file.filename)
        storage_path = self._upload_to_bucket(content, filename=file.filename, user_id=user_id, content_type=content_type)

        document = DocumentCreate(
            user_id = user_id,
            title = title,
            original_filename = file.filename,
            storage_path = storage_path,
            file_size=len(content),
            file_type=content_type,
            source_type=source_type,
            content_hash=content_hash,
            source_id=None,
            chunk_count=0
        )

        db_document = await self.document_repository.create_document(document)

        return db_document



    def _calculate_hash(self, content:bytes) ->str:
        hashed_string = hashlib.sha256(content).hexdigest()
        return hashed_string

    def _create_title_from_file(self, filename) ->str:
        title=filename.replace(" ", "").split(".")[0] 
        return title       

    def _get_source_type_from_file(self, filename) ->str:
        title=filename.replace(" ", "").split(".")[-1] 
        return title    

    def _upload_to_bucket(self, content:bytes, filename:str, user_id:int, content_type:str) ->str:
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



