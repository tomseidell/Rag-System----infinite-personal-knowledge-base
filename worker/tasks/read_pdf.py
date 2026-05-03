import gc
import logging

from celery import Task
from celery.exceptions import SoftTimeLimitExceeded

from shared.database import SyncSessionLocal
from worker.celery_app import celery_app
from worker.clients.redis_service import RedisService
from worker.document.document_repository import DocumentRepositorySync
from worker.document.document_service import DocumentService
from worker.document.exceptions import PDFProcessingException, TextSplittingException

logger = logging.getLogger(__name__)


@celery_app.task(
    name="read_pdf", # queue
    autoretry_for=(PDFProcessingException, TextSplittingException),
    max_retries=2,
    bind=True,
    soft_time_limit=120,
    time_limit=150,
    retry_backoff=True,
)
def read_pdf(
    self: Task,
    encoded_content: str,
    document_id: int,
    user_id: int,
    filename: str,
    content_type: str,
):
    # dependencies:
    db = SyncSessionLocal()
    redis_service = RedisService()
    document_repo = DocumentRepositorySync(db=db)
    document_service = DocumentService(repository=document_repo)

    try:
        logger.info(f"PDF reader started for document {document_id}")
        redis_service.set_status(document_id, "reading_pdf", "Extracting text from PDF")

        text = document_service.extract_text_from_pdf(content=encoded_content)

        redis_service.set_status(document_id, "chunking", "Chunking text")
        chunks = document_service.split_text(text)

        celery_app.send_task(
            "embed_document",
            args=[encoded_content, document_id, user_id, filename, content_type, chunks],
            queue="embed",
        )

        logger.info(f"Document {document_id} sent to embedding worker")

    except (PDFProcessingException, TextSplittingException) as e:
        logger.error(f"PDF processing failed for document {document_id}: {e}")
        redis_service.set_status(document_id, "failed", str(e))
        db.rollback()
        document_repo.mark_status_failed(
            document_id=document_id,
            user_id=user_id,
            error_message="Failed to read PDF, please try again later",
        )
        raise

    except SoftTimeLimitExceeded:
        logger.error(f"PDF reader timed out for document {document_id}")
        redis_service.set_status(document_id, "failed", "Timeout while reading PDF")
        db.rollback()
        document_repo.mark_status_failed(
            document_id=document_id,
            user_id=user_id,
            error_message="Timeout while reading PDF",
        )
        raise

    except Exception as e:
        logger.error(f"Unexpected error in PDF reader for document {document_id}: {e}", exc_info=True)
        redis_service.set_status(document_id, "failed", "Unexpected error")
        db.rollback()
        document_repo.mark_status_failed(
            document_id=document_id,
            user_id=user_id,
            error_message="Unexpected error while reading PDF",
        )
        raise

    finally:
        db.close()
        gc.collect()
