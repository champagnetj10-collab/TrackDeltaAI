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
    # Routing — all tasks go to the "default" queue for now. task_default_queue
    # must match, or `celery worker` (no -Q flag) only ever consumes Celery's
    # own default queue name ("celery") and every task routed here sits
    # unconsumed forever — this was a real bug caught only once a worker
    # actually ran against production Redis for the first time.
    task_default_queue="default",
    task_routes={
        "pipeline.tasks.process_session.process_session_task": {"queue": "default"},
    },
    # Local dev convenience: run tasks synchronously, no broker/worker needed.
    task_always_eager=settings.celery_task_always_eager,
    task_eager_propagates=settings.celery_task_always_eager,
)
