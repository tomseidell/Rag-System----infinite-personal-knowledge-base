import uuid
from fastapi import UploadFile
from shared.modules.document.model import Document
from api.modules.document.repository import DocumentRepository
import hashlib
from api.modules.document.schemas import DocumentCreate, PaginatedDocuments, DocumentUploadResponse, DocumentContentResponse, DocumentResponse
from pathlib import Path
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from celery.result import AsyncResult



from shared.core.exceptions import InputError, NotFoundException

from api.clients.storage.service import AsyncStorageService
from api.modules.user.repository import UserRepository

#from worker.tasks.process_document import process_document

from api.clients.qdrant.service import AsyncQdrantService

from api.modules.chunk.service import ChunkServiceAsync

import base64

from worker.celery_app import celery_app




class DocumentService:
    def __init__(self, document_repository:DocumentRepository, storage:AsyncStorageService, user_repository:UserRepository, qdrant_service:AsyncQdrantService, chunk_service:ChunkServiceAsync, db:AsyncSession):
        self.document_repository = document_repository
        self.storage = storage
        self.user_repository = user_repository
        self.qdrant = qdrant_service
        self.chunk_service = chunk_service
        self.db = db

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
        
        # random id
        unique_id = uuid.uuid4()
        
        return f"{unique_id}_{name}{ext}" 

    def _encode_content_base64(self, content:bytes) ->str:
        encoded_bytes = base64.b64encode(content)
        return encoded_bytes.decode("utf-8")


    async def upload_document(self, user_id: int, title: str| None, file:UploadFile) -> DocumentUploadResponse:
        content = await file.read()#bytes, runs in separate threadpool
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

        source_type = self._get_file_extension(filename=file.filename)

        if source_type != "pdf":
            raise InputError(
                operation="upload_document",
                detail="inserted file is not pdf"
            )

        name = self._generate_unique_filename(filename=file.filename)

        # create unique hash acting as identifier for each document 
        content_hash = await asyncio.to_thread(self._calculate_hash, content) # asyncio to move task to different thread

        # check if document with hash is already stored in db
        existing = await self.document_repository.check_for_existing_hash(user_id=user_id, content_hash=content_hash)

        if existing: #do not save document if already existing 
            return DocumentUploadResponse.model_validate(existing) 

        if not title: # if no title provided, create title automatically based on filename
            title = self._create_title_from_file(filename=file.filename)

        document = DocumentCreate(
            user_id = user_id,
            title = title,
            original_filename = file.filename,
            file_size=len(content),
            file_type=content_type,
            source_type=source_type,
            content_hash=content_hash,
        )

        db_document = await self.document_repository.create_document(document)

        # change binary image format to base64
        encoded_content = await asyncio.to_thread(self._encode_content_base64, content)

        # call celery worker task
        result:AsyncResult = await asyncio.to_thread(
            celery_app.send_task,
            "process_document",
            args=[encoded_content, db_document.id, user_id, name, content_type]
        )

        task_id = result.task_id

        print("task Id 🆔: ",task_id)

        response = DocumentUploadResponse.model_validate(db_document)
        response.task_id = task_id

        return response


    async def get_document(self, user_id:int, document_id:int) -> DocumentContentResponse:
        document = await self.document_repository.get_document(user_id=user_id, document_id=document_id)
        if document is None:
            raise NotFoundException("document")
        content = await self.storage.get_file(storage_path=document.storage_path)
        return DocumentContentResponse(id=document.id, content=content, original_filename=document.original_filename, file_type=document.file_type, file_size=document.file_size, )


    async def delete_document(self, user_id:int, document_id:int) ->None:
        try:
            document = await self.document_repository.get_document(user_id=user_id, document_id=document_id)
            if document is None:
                raise NotFoundException("document")
            chunks_ids = await self.chunk_service.get_chunks_for_doc(document_id=document_id, user_id=user_id)
            await self.document_repository.delete_document(user_id=user_id, document_id=document_id)

            tasks = []

            if chunks_ids:
                await self.chunk_service.delete_chunks_for_doc(user_id=user_id, document_id=document_id)
                tasks.append(self.qdrant.delete_many_chunks(chunk_ids=chunks_ids))
            
            if document.storage_path:
                tasks.append(self.storage.delete_file(document.storage_path))
                
            await asyncio.gather(*tasks)

            await self.db.commit()

        except NotFoundException:
            raise


        except Exception:
            await self.db.rollback()
            raise


    async def get_documents(self, user_id:int, cursor:int | None)-> PaginatedDocuments:
        documents, cursor = await self.document_repository.get_documents(user_id, cursor)
        return PaginatedDocuments(
            documents=[DocumentResponse.model_validate(document) for document in documents],
            next_cursor=cursor
        )
    

    async def get_document_name_and_id(self, user_id:int, document_id:int)->tuple[int, str]:
        document = await self.document_repository.get_document(user_id=user_id, document_id=document_id)
        if document is None:
            raise NotFoundException("document")
        return document.id, document.original_filename