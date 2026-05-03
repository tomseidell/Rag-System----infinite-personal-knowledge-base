import os

from celery import Celery
from celery.signals import worker_process_init
from functools import lru_cache

from shared.modules.chunk.model import Chunk
from shared.modules.document.model import Document
from shared.modules.user.model import User

from worker.clients.qdrant_service import QdrantService

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379"),
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "read_pdf": {"queue": "pdf_read"}, # worker 1 listening on pdf read
        "embed_document": {"queue": "embed"}, # worker 2 listening on embed
    },
)

celery_app.autodiscover_tasks(["worker.tasks"]) # search for tasks in directory


@lru_cache()
def get_qdrant_service():
    print("loading Sparse embedding model")
    return QdrantService()


# only load the heavy Qdrant/embedding model on the embedder worker
@worker_process_init.connect
def init_models(**kwargs):
    if os.getenv("WORKER_TYPE") == "embedder":
        get_qdrant_service()


from worker.tasks.process_document import embed_document
from worker.tasks.read_pdf import read_pdf
