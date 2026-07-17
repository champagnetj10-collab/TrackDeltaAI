"""Celery worker definition.

Start with:
    celery -A pipeline.worker worker --loglevel=info

In development with Docker Compose:
    docker compose up worker
"""

from celery import Celery

# Import every model so SQLAlchemy's declarative registry knows about all
# of them before any task runs — same reason alembic/env.py does this.
# process_session_task only directly imports Session/DriverDNA/Debrief,
# but Session.user_id's ForeignKey("users.id") can't resolve unless
# app.models.user has been imported somewhere in this process too, which
# nothing else in the worker's import graph does. Surfaced as
# NoReferencedTableError the first time a task actually ran against a
# real worker process.
import app.models.debrief  # noqa: F401
import app.models.dna  # noqa: F401
import app.models.session  # noqa: F401
import app.models.subscription_event  # noqa: F401
import app.models.track  # noqa: F401
import app.models.user  # noqa: F401
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
