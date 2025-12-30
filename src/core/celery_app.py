from celery import Celery
import os
from celery.signals import worker_process_init
from functools import lru_cache
from src.clients.qdrant.service import QdrantService


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
    #worker_max_tasks_per_child = 10, # kill the worker after 10 tasks
    task_routes={
        "src.modules.document.workers.*": {"queue": "documents"},
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