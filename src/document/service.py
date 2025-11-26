import uuid
from fastapi import UploadFile
from src.document.model import Document
from src.document.repository import DocumentRepository
import hashlib
from src.document.schemas import DocumentCreate
from pathlib import Path


from src.core.exceptions import InputError, NotFoundException

from src.storage.service import StorageService
from src.user.repository import UserRepository


class DocumentService:
    def __init__(self, document_repository:DocumentRepository, storage:StorageService, user_repository:UserRepository):
        self.document_repository = document_repository
        self.storage = storage
        self.user_repository = user_repository

# private methods
    def _calculate_hash(self, content:bytes) ->str:
        hashed_string = hashlib.sha256(content).hexdigest()
        return hashed_string

    def _create_title_from_file(self, filename:str) ->str:
        title=filename.replace(" ", "").split(".")[0] 
        return title       

    def _get_file_extension(self, filename:str) ->str:
        extenstion = filename.replace(" ", "").split(".")[-1] 
        return extenstion   

    def _generate_unique_filename(self, filename:str) ->str:
        path = Path(filename)
        name = path.stem  # "document"
        ext = path.suffix  # ".pdf"
        
        unique_id = uuid.uuid4()
        
        return f"{unique_id}_{name}{ext}" 


    async def upload_document(self, user_id: int, title: str| None, file:UploadFile) -> Document:
        content = await file.read()
        if len(content) >= 10 * 1024 * 1024: #10mb max
            raise InputError(
                operation="upload_document",
                detail= "File is too large"
            )

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

        source_type = self._get_file_extension(filename=file.filename)
        name = self._generate_unique_filename(filename=file.filename)
        storage_path = self.storage.upload_file(content, filename=name, user_id=user_id, content_type=content_type)

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


    async def get_document(self, user_id:int, document_id:int) -> tuple[bytes, str, str]:
        document = await self.document_repository.get_document(user_id=user_id, document_id=document_id)
        if document is None:
            raise NotFoundException("document")
        content = self.storage.get_file(storage_path=document.storage_path)
        return content, document.original_filename, document.file_type


