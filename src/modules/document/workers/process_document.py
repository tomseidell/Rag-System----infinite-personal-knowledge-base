from src.modules.document.model import Document
from src.modules.chunk.model import Chunk
from src.modules.user.model import User
import os 
import ollama
from src.database import SyncSessionLocal
from src.clients.storage.service import StorageService
from src.clients.qdrant.service import QdrantService
from src.clients.ollama.service import OllamaService
from src.modules.chunk.service import ChunkServiceSync
from src.modules.chunk.repository import ChunkRepositorySync
from src.modules.document.repository import DocumentRepositorySync
from src.modules.document.utils.pdf_processing import extract_text_from_pdf
from src.modules.document.utils.split_text_to_chunks import split_text

import logging
from src.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def process_document(content:bytes, document_id:int, user_id:int, filename:str, content_type:str):

    
    db = SyncSessionLocal()
    storage_service = StorageService()
    qdrant_service = QdrantService()
    ollama_service = OllamaService()
    chunk_repo = ChunkRepositorySync(db=db)
    chunk_service = ChunkServiceSync(repo=chunk_repo)
    document_repo = DocumentRepositorySync(db=db)
    storage_path = None
    chunk_ids = []
    try:
        text = extract_text_from_pdf(content=content)
        chunks = split_text(text)
        embeddings = ollama_service.embed_text(chunks=chunks)
        chunk_objects: list[Chunk] = chunk_service.create_chunks_from_text(chunks=chunks, user_id=user_id, document_id=document_id)



        result = qdrant_service.insert_many_chunks(chunk_objects=chunk_objects, embeddings=embeddings)

        chunk_ids = result.chunk_ids

        storage_path = storage_service.upload_file(
            content=content,
            filename=filename,
            user_id=user_id,
            content_type=content_type
        )

        document_repo.finish_document(document_id=document_id, user_id=user_id, storage_path=storage_path, chunk_count=len(chunk_ids))

    except Exception as e:
        db.rollback()

        if chunk_ids:
            qdrant_service.delete_many_chunks(chunkIds=chunk_ids)

        if storage_path: # delete from gcp storage 
            storage_service.delete_file(storage_path)

        document_repo.mark_status_failed(document_id=document_id, user_id=user_id)

        raise
    
    finally:
        db.close()



