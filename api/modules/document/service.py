import uuid
from fastapi import UploadFile
from app.modules.document.model import Document
from app.modules.document.repository import DocumentRepository
import hashlib
from app.modules.document.schemas import DocumentCreate, GetDocuments
from pathlib import Path
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.exceptions import InputError, NotFoundException

from app.clients.storage.service import StorageService
from app.modules.user.repository import UserRepository

from app.modules.document.workers.process_document import process_document

from app.clients.qdrant.service import AsyncQdrantService

from app.modules.chunk.dependencies import ChunkServiceAsync

import base64



class DocumentService:
    def __init__(self, document_repository:DocumentRepository, storage:StorageService, user_repository:UserRepository, qdrant_service:AsyncQdrantService, chunk_service:ChunkServiceAsync, db:AsyncSession):
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



    async def upload_document(self, user_id: int, title: str| None, file:UploadFile) -> Document:
        content = await file.read()#bytes
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

        # create unique hash acting as identifier for each document 
        content_hash = self._calculate_hash(content=content)

        # check if document with hash is already stored in db
        existing = await self.document_repository.check_for_existing_hash(user_id=user_id, content_hash=content_hash)

        if existing: #do not save document if already existing 
            return existing 

        if not title: # if no title provided, create title automatically based on filename
            title = self._create_title_from_file(filename=file.filename)

        source_type = self._get_file_extension(filename=file.filename)
        name = self._generate_unique_filename(filename=file.filename)

        if source_type != "pdf":
            raise InputError(
                operation="upload_document",
                detail="inserted file is not pdf"
            )

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

        encoded_content = base64.b64encode(content).decode('utf-8')
        process_document.delay(content=encoded_content, document_id=db_document.id, user_id = user_id, filename=name, content_type=content_type)

        return db_document

    async def get_document(self, user_id:int, document_id:int) -> tuple[bytes, str, str]:
        document = await self.document_repository.get_document(user_id=user_id, document_id=document_id)
        if document is None:
            raise NotFoundException("document")
        content = self.storage.get_file(storage_path=document.storage_path)
        return content, document.original_filename, document.file_type

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
                tasks.append(asyncio.to_thread(self.storage.delete_file, document.storage_path))

                
            await asyncio.gather(*tasks)

            await self.db.commit()

        except NotFoundException:
            raise


        except Exception:
            await self.db.rollback()
            raise


    async def get_documents(self, user_id:int, cursor:int | None)-> tuple[list[Document], int | None]:
        result = await self.document_repository.get_documents(user_id, cursor)
        return result
    

    async def get_document_name_and_id(self, user_id:int, document_id:int):
        document = await self.document_repository.get_document(user_id=user_id, document_id=document_id)
        if document is None:
            raise NotFoundException("document")
        return document.id, document.original_filename