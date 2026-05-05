import base64
import gc
import logging

from celery import Task
from celery.exceptions import SoftTimeLimitExceeded

from shared.database import SyncSessionLocal
from shared.modules.chunk.model import Chunk
from shared.modules.user.model import User  
from shared.modules.document.model import Document  
from shared.core.exceptions import OllamaException, QdrantException, StorageException, OpenaiException

from worker.celery_app import celery_app
from worker.clients.redis_service import RedisService
from worker.clients.storage_service import StorageService
from worker.clients.qdrant_service import QdrantService
from worker.clients.llm.dependency import get_llm_service
from worker.chunk.chunk_repository import ChunkRepositorySync
from worker.chunk.chunk_service import ChunkServiceSync
from worker.document.document_repository import DocumentRepositorySync

logger = logging.getLogger(__name__)


@celery_app.task(
    name="embed_document",
    autoretry_for=(OllamaException, QdrantException, StorageException),
    max_retries=3,
    bind=True,
    soft_time_limit=300,
    time_limit=350,
    retry_backoff=True,
)
def embed_document(
    self: Task,
    encoded_content: str,
    document_id: int,
    user_id: int,
    filename: str,
    content_type: str,
    chunks: list[str],
):
    
    # dependencies:
    db = SyncSessionLocal()
    storage_service = StorageService()
    qdrant_service = QdrantService()
    llm_service = get_llm_service()
    redis_service = RedisService()
    chunk_repo = ChunkRepositorySync(db=db)
    chunk_service = ChunkServiceSync(repo=chunk_repo)
    document_repo = DocumentRepositorySync(db=db)

    # global vars
    storage_path = None
    chunk_ids = []

    try:
        logger.info(f"Embedder started for document {document_id} ({len(chunks)} chunks)")
        redis_service.set_status(document_id, "embedding", "Embedding document")

        chunk_objects: list[Chunk] = chunk_service.create_chunks_from_text(
            chunks=chunks,
            user_id=user_id,
            document_id=document_id,
        )

        dense_embeddings = llm_service.embed_text(chunks=chunks)

        sparse_embeddings = qdrant_service.create_sparse_embedding(chunks)

        qdrant_insert_result = qdrant_service.insert_chunks(
            chunk_objects=chunk_objects,
            dense_embeddings=dense_embeddings,
            sparse_embeddings=sparse_embeddings,
        )

        # clean ram of worker
        del chunks, sparse_embeddings, dense_embeddings, chunk_objects
        gc.collect()

        chunk_ids = qdrant_insert_result.chunk_ids


        # upload to bucket
        storage_path = storage_service.upload_file(
            content=base64.b64decode(encoded_content),
            filename=filename,
            user_id=user_id,
            content_type=content_type,
        )

        del encoded_content
        gc.collect()

        # save completed document to db
        document_repo.finish_document(
            document_id=document_id,
            user_id=user_id,
            storage_path=storage_path,
            chunk_count=len(chunk_ids),
        )

        redis_service.set_status(document_id, "completed", "Document processed")
        logger.info(f"Document {document_id} processed successfully")

    except (OllamaException, QdrantException, StorageException, OpenaiException) as e:
        logger.error(f"Service exception for document {document_id}: {e}")
        redis_service.set_status(document_id, "failed", str(e))
        db.rollback()
        if chunk_ids:
            qdrant_service.delete_many_chunks(chunkIds=chunk_ids)
        if storage_path:
            storage_service.delete_file(storage_path)
        if self.request.retries == self.max_retries:
            document_repo.mark_status_failed(
                document_id=document_id,
                user_id=user_id,
                error_message="Processing failed, please try again later",
            )
        raise

    except SoftTimeLimitExceeded:
        logger.error(f"Embedder timed out for document {document_id}")
        redis_service.set_status(document_id, "failed", "Timeout during embedding")
        db.rollback()
        if chunk_ids:
            qdrant_service.delete_many_chunks(chunkIds=chunk_ids)
        if storage_path:
            storage_service.delete_file(storage_path)
        document_repo.mark_status_failed(
            document_id=document_id,
            user_id=user_id,
            error_message="Timeout during processing",
        )
        raise

    except Exception as e:
        logger.error(f"Unexpected error for document {document_id}: {e}", exc_info=True)
        redis_service.set_status(document_id, "failed", "Unexpected error")
        db.rollback()
        if chunk_ids:
            qdrant_service.delete_many_chunks(chunkIds=chunk_ids)
        if storage_path:
            storage_service.delete_file(storage_path)
        document_repo.mark_status_failed(
            document_id=document_id,
            user_id=user_id,
            error_message="Unexpected error during processing",
        )
        raise

    finally:
        db.close()
        gc.collect()
