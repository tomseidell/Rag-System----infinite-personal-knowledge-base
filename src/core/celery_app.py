from celery import Celery
import os
from celery.signals import worker_process_init
from functools import lru_cache
from src.clients.qdrant.service import QdrantService


celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379"), # where to push tasks
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379"), # where to save tasks
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={ 
        "src.modules.document.workers.*": {"queue": "documents"}, # if called funcion is in relative path to key, task should go to documents queue
    }
)

# cache qdrant_service instance in get_qdrant_service function 
@lru_cache()
def get_qdrant_service():
    print("loading Sparse embedding model")
    qdrant_service = QdrantService()
    return qdrant_service
    
# immediately after initializing celery worker, call get_qdrant_service
@worker_process_init.connect
def init_models(**kwargs):
    get_qdrant_service()

from src.modules.document.workers import process_document  