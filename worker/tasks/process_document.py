import gc
import logging

from celery import Task
from celery.exceptions import SoftTimeLimitExceeded

from shared.database import SyncSessionLocal
from shared.modules.chunk.model import Chunk

from worker.celery_app import celery_app

from worker.chunk.chunk_repository import ChunkRepositorySync
from worker.chunk.chunk_service import ChunkServiceSync

from worker.document.document_repository import DocumentRepositorySync
from worker.document.document_service import DocumentService

from shared.core.exceptions import OllamaException, QdrantException, StorageException
from worker.clients.storage_service import StorageService
from worker.clients.qdrant_service import QdrantService
from worker.clients.ollama_service import OllamaService

logger = logging.getLogger(__name__)

print("load task")


@celery_app.task(
    name="process_document",
    autoretry_for=(OllamaException, QdrantException, StorageException), # if exception occurs, celery re- adds task to redis to perform retry
    max_retries=3,
    bind=True,
    soft_time_limit=300, # retry logic
    time_limit= 350, # mark task as failed
    retry_backoff = True # increase time between retries exponentially 
)
def process_document(self: Task, content: bytes, document_id: int, user_id: int, filename: str, content_type: str):
    db = SyncSessionLocal()
    storage_service = StorageService()
    qdrant_service = QdrantService()
    ollama_service = OllamaService()
    chunk_repo = ChunkRepositorySync(db=db)
    chunk_service = ChunkServiceSync(repo=chunk_repo)
    document_repo = DocumentRepositorySync(db=db)
    document_service = DocumentService(repository=document_repo)
    document_service.log_memory("After Services Init")

    storage_path = None
    chunk_ids = []

    try:
        logger.info(f"Processing document {document_id} ({filename})")
        document_service.log_memory(f"Content received ({len(content)} bytes)")

        text = document_service.extract_text_from_pdf(content=content)
        document_service.log_memory(f"After Text Extraction ({len(text)} chars)")

        chunks = document_service.split_text(text)
        document_service.log_memory(f"After Chunking ({len(chunks)} chunks)")

        # remove variable to keep ram efficient 
        del text
        gc.collect()
        document_service.log_memory("After Text Cleanup")
        
        # create dense embeddings 
        dense_embeddings = ollama_service.embed_text(chunks=chunks)
        document_service.log_memory(f"After Embeddings ({len(dense_embeddings)} vectors)")
        
        # save chunks to database
        chunk_objects: list[Chunk] = chunk_service.create_chunks_from_text(
            chunks=chunks, 
            user_id=user_id, 
            document_id=document_id
        )
        document_service.log_memory(f"After saving chunks to db ({len(chunk_objects)} objects)")

        
        # create sparse embeddings and save chunks in vector db
        sparse_embeddings = qdrant_service.create_sparse_embedding(chunks)

        # safe chunks to vector db
        qdrant_insert_result = qdrant_service.insert_chunks(chunk_objects=chunk_objects, dense_embeddings=dense_embeddings, sparse_embeddings=sparse_embeddings )

        del chunks
        gc.collect()
        document_service.log_memory("After Chunks Cleanup")

        chunk_ids = qdrant_insert_result.chunk_ids
        document_service.log_memory(f"After Qdrant Insert ({len(chunk_ids)} inserted)")
        del dense_embeddings, chunk_objects
        gc.collect()
        document_service.log_memory("After Embeddings Cleanup")
        
        # upload file to gcp bucket 
        storage_path = storage_service.upload_file(
            content=content,
            filename=filename,
            user_id=user_id,
            content_type=content_type
        )
        document_service.log_memory("After Storage Upload")
        
        # delete the bytes 
        del content
        gc.collect()
        document_service.log_memory("After Content Cleanup")
        
        # mark document as finished in db documents table 
        document_repo.finish_document(
            document_id=document_id, 
            user_id=user_id, 
            storage_path=storage_path, 
            chunk_count=len(chunk_ids)
        )
        document_service.log_memory("After DB Update")
        
        logger.info(f"Document {document_id} processed successfully!")
        document_service.log_memory("Task Success")

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
        document_service.log_memory("Task End")



