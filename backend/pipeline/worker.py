"""Celery worker definition.

Start with:
    celery -A pipeline.worker worker --loglevel=info

In development with Docker Compose:
    docker compose up worker
"""

from celery import Celery

from app.config import settings

celery_app = Celery(
    "trackdelta",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["pipeline.tasks.process_session"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Retry failed tasks up to 3 times with exponential back-off
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=30,
    task_max_retries=3,
    # Visibility timeout slightly longer than the longest expected task
    broker_transport_options={"visibility_timeout": 3600},
    # Routing — all tasks go to the default queue for now
    task_routes={
        "pipeline.tasks.process_session.process_session_task": {"queue": "default"},
    },
)
