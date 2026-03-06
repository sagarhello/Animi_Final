from celery import Celery
from app.config import settings

celery_app = Celery(
    "animface",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.workers.tasks.convert_video_to_anime": {"queue": "anime_conversion"},
    },
    # Long videos + stronger stylization can exceed 6 minutes.
    # Keep hard limit above soft limit so the task can handle timeout gracefully.
    task_soft_time_limit=1200,  # 20 min soft limit
    task_time_limit=1440,       # 24 min hard limit
)
