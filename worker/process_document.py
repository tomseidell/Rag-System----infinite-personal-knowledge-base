import gc
import logging

from celery import Task
from celery.exceptions import SoftTimeLimitExceeded

from shared.database import SyncSessionLocal
from shared.modules.chunk.model import Chunk
from worker.utils.document.log_memory import log_memory
from worker.utils.document.pdf_processing import extract_text_from_pdf
from worker.utils.document.split_text_to_chunks import split_text

from worker.celery_app import celery_app
from worker.repositories import ChunkRepositorySync, DocumentRepositorySync
from worker.services import ChunkServiceSync

from shared.core.exceptions import OllamaException, QdrantException, StorageException
from worker.clients.storage_service import StorageService
from worker.clients.qdrant_service import QdrantService
from worker.clients.ollama_service import OllamaService

logger = logging.getLogger(__name__)


@celery_app.task(
    autoretry_for=(OllamaException, QdrantException, StorageException), # if exception occurs, celery re- adds task to redis to perform retry
    max_retries=3,
    bind=True,
    soft_time_limit=300, # retry logic
    time_limit= 350, # mark task as failed
    retry_backoff = True # increase time between retries exponentially 
)
def process_document(self: Task, content: bytes, document_id: int, user_id: int, filename: str, content_type: str):
    log_memory("Task Start")
    db = SyncSessionLocal()
    storage_service = StorageService()
    qdrant_service = QdrantService()
    ollama_service = OllamaService()
    chunk_repo = ChunkRepositorySync(db=db)
    chunk_service = ChunkServiceSync(repo=chunk_repo)
    document_repo = DocumentRepositorySync(db=db)
    log_memory("After Services Init")

    storage_path = None
    chunk_ids = []

    try:
        logger.info(f"Processing document {document_id} ({filename})")
        log_memory(f"Content received ({len(content)} bytes)")

        text = extract_text_from_pdf(content=content)
        log_memory(f"After Text Extraction ({len(text)} chars)")

        chunks = split_text(text)
        log_memory(f"After Chunking ({len(chunks)} chunks)")

        # remove variable to keep ram efficient 
        del text
        gc.collect()
        log_memory("After Text Cleanup")
        
        # create dense embeddings 
        dense_embeddings = ollama_service.embed_text(chunks=chunks)
        log_memory(f"After Embeddings ({len(dense_embeddings)} vectors)")
        
        # save chunks to database
        chunk_objects: list[Chunk] = chunk_service.create_chunks_from_text(
            chunks=chunks, 
            user_id=user_id, 
            document_id=document_id
        )
        log_memory(f"After saving chunks to db ({len(chunk_objects)} objects)")

        
        # create sparse embeddings and save chunks in vector db
        sparse_embeddings = qdrant_service.create_sparse_embedding(chunks)

        # safe chunks to vector db
        qdrant_insert_result = qdrant_service.insert_chunks(chunk_objects=chunk_objects, dense_embeddings=dense_embeddings, sparse_embeddings=sparse_embeddings )

        del chunks
        gc.collect()
        log_memory("After Chunks Cleanup")

        chunk_ids = qdrant_insert_result.chunk_ids
        log_memory(f"After Qdrant Insert ({len(chunk_ids)} inserted)")
        del dense_embeddings, chunk_objects
        gc.collect()
        log_memory("After Embeddings Cleanup")
        
        # upload file to gcp bucket 
        storage_path = storage_service.upload_file(
            content=content,
            filename=filename,
            user_id=user_id,
            content_type=content_type
        )
        log_memory("After Storage Upload")
        
        # delete the bytes 
        del content
        gc.collect()
        log_memory("After Content Cleanup")
        
        # mark document as finished in db documents table 
        document_repo.finish_document(
            document_id=document_id, 
            user_id=user_id, 
            storage_path=storage_path, 
            chunk_count=len(chunk_ids)
        )
        log_memory("After DB Update")
        
        logger.info(f"Document {document_id} processed successfully!")
        log_memory("Task Success")

    # retry for 3 error types
    except (OllamaException, QdrantException, StorageException) as e:
        logger.error(f"Service exception: {e}")
        db.rollback()
        
        if chunk_ids:
            qdrant_service.delete_many_chunks(chunkIds=chunk_ids)
        if storage_path:
            storage_service.delete_file(storage_path)
        if self.request.retries == self.max_retries:
            document_repo.mark_status_failed(
                document_id=document_id, 
                user_id=user_id, 
                error_message="Saving document failed, please try again later"
            )
        raise

    # mark task as failed when having too many retries
    except SoftTimeLimitExceeded:
        logger.error("Task timeout!")
        db.rollback()
        if chunk_ids:
            qdrant_service.delete_many_chunks(chunkIds=chunk_ids)
        if storage_path:
            storage_service.delete_file(storage_path)
        document_repo.mark_status_failed(
            document_id=document_id, 
            user_id=user_id, 
            error_message="Timeout in operation"
        )
        raise

    # when unexcpected error occurs, stop and rollback
    except Exception as e:
        logger.error(f"Unexpected exception: {e}", exc_info=True)
        db.rollback()
        if chunk_ids:
            qdrant_service.delete_many_chunks(chunkIds=chunk_ids)
        if storage_path:
            storage_service.delete_file(storage_path)
        document_repo.mark_status_failed(
            document_id=document_id, 
            user_id=user_id, 
            error_message="Saving document failed, please try again later"
        )
        raise
    
    finally:
        db.close()
        gc.collect()
        log_memory("Task End")



