"""
Celery Tasks — Anime Video Conversion
The heavy lifting happens here, in a background worker.
"""
import uuid
from datetime import datetime
from celery import current_task
from billiard.exceptions import SoftTimeLimitExceeded
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.workers.celery_app import celery_app
from app.config import settings
from app.models.video import Video, VideoStatus
from app.services.anime_pipeline import anime_pipeline
from app.services.storage_service import storage


def get_sync_db():
    """Sync DB session for Celery (no async in workers)."""
    engine = create_engine(settings.SYNC_DATABASE_URL)
    with Session(engine) as session:
        yield session


@celery_app.task(
    name="app.workers.tasks.convert_video_to_anime",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
)
def convert_video_to_anime(self, video_id: str):
    """
    Main task: converts uploaded video to anime style.
    Steps:
      1. Load video record from DB
      2. Update status → PROCESSING
      3. Run anime pipeline
      4. Save output paths to DB
      5. Delete original (privacy)
      6. Update status → READY
    """
    vid_uuid = uuid.UUID(video_id)
    logger.info(f"[Task {self.request.id}] Starting anime conversion for video {video_id}")

    engine = create_engine(settings.SYNC_DATABASE_URL)

    with Session(engine) as db:
        video = db.get(Video, vid_uuid)
        if not video:
            logger.error(f"Video {video_id} not found")
            return {"error": "Video not found"}

        # ─── Mark as processing ───────────────────────────────────────────
        video.status = VideoStatus.PROCESSING
        video.celery_task_id = self.request.id
        video.processing_started_at = datetime.utcnow()
        video.processing_progress = 5
        db.commit()

        # ─── Paths ───────────────────────────────────────────────────────
        original_path = video.original_path
        animated_path = storage.get_animated_path(vid_uuid)
        thumbnail_path = storage.get_thumbnail_path(vid_uuid)

        def progress_callback(pct: int, stage: str):
            """Update DB progress during processing."""
            stage_map = {
                "face_detection": VideoStatus.FACE_DETECTION,
                "animating": VideoStatus.ANIMATING,
                "privacy_strip": VideoStatus.PRIVACY_STRIP,
                "ready": VideoStatus.READY,
            }
            with Session(engine) as inner_db:
                v = inner_db.get(Video, vid_uuid)
                if v:
                    v.processing_progress = pct
                    if stage in stage_map:
                        v.status = stage_map[stage]
                    inner_db.commit()

            # Update Celery task state for real-time polling
            current_task.update_state(
                state="PROGRESS",
                meta={"progress": pct, "stage": stage}
            )

        try:
            # ─── Run the pipeline ─────────────────────────────────────────
            result = anime_pipeline.process_video(
                input_path=original_path,
                output_path=animated_path,
                thumbnail_path=thumbnail_path,
                anime_style=video.anime_style.value,
                progress_callback=progress_callback,
            )

            # ─── Update video record with results ─────────────────────────
            video.animated_path = storage.get_public_url(animated_path)
            video.animated_filename = f"{video_id}_anime.mp4"
            video.thumbnail_path = storage.get_public_url(thumbnail_path)
            video.faces_detected = result["faces_detected"]
            video.original_duration_sec = result["duration_sec"]
            video.width = result["width"]
            video.height = result["height"]
            video.fps = result["fps"]
            video.processing_duration_sec = result["processing_duration_sec"]
            video.processing_progress = 100
            video.status = VideoStatus.READY
            video.processing_completed_at = datetime.utcnow()
            db.commit()

            # ─── Delete original (PRIVACY) ────────────────────────────────
            import asyncio
            loop = asyncio.new_event_loop()
            deleted = loop.run_until_complete(storage.delete_original(original_path))
            loop.close()

            if deleted:
                video.original_path = None
                video.original_deleted = True
                db.commit()
                logger.info(f"Original video deleted for privacy: {original_path}")

            logger.info(f"[Task {self.request.id}] Conversion complete for {video_id}")
            return {"status": "ready", "video_id": video_id, "faces": result["faces_detected"]}

        except SoftTimeLimitExceeded:
            timeout_message = (
                "Video processing timed out. Try a shorter video, lower resolution, "
                "or retry with fewer conversions running in parallel."
            )
            logger.error(f"[Task {self.request.id}] Soft time limit exceeded for video {video_id}")
            video.status = VideoStatus.FAILED
            video.error_message = timeout_message
            video.processing_completed_at = datetime.utcnow()
            db.commit()
            return {"error": timeout_message}

        except Exception as exc:
            logger.error(f"[Task {self.request.id}] Pipeline failed: {exc}")
            video.status = VideoStatus.FAILED
            video.error_message = str(exc)
            video.processing_completed_at = datetime.utcnow()
            db.commit()

            # Retry up to 2 times
            try:
                raise self.retry(exc=exc, countdown=30)
            except self.MaxRetriesExceededError:
                logger.error(f"Max retries exceeded for video {video_id}")
                return {"error": str(exc)}
