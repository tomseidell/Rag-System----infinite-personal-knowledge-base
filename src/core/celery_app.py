from celery import Celery
import os

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
    worker_max_tasks_per_child = 10, # kill the worker after 10 tasks
    task_routes={
        "src.modules.document.workers.*": {"queue": "documents"},
    }
)

from src.modules.document.workers import process_document  