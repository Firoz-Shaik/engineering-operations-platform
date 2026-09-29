from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "operations_api",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.deployments"],
)
celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    result_expires=86400,
    broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=1,
)