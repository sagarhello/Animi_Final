import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.video import Video, VideoStatus, AnimeStyle
from app.schemas.video import VideoOut, VideoStatusOut
from app.services.storage_service import storage
from app.core.dependencies import get_current_user
from app.workers.tasks import convert_video_to_anime
from app.config import settings
from loguru import logger

router = APIRouter(prefix="/videos", tags=["Videos"])


@router.post("/upload", response_model=VideoOut, status_code=201)
async def upload_video(
    file: UploadFile = File(...),
    anime_style: AnimeStyle = Form(AnimeStyle.ANIME),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a video for anime conversion.
    1. Validates file type and size
    2. Saves to local storage (encrypted in production)
    3. Creates DB record
    4. Dispatches Celery task for background processing
    5. Returns video record immediately (poll /videos/{id}/status for progress)
    """
    # ─── Validate ─────────────────────────────────────────────────────────
    storage.validate_video_file(file)

    # Check size via content-length header (quick check)
    if getattr(file, "size", None) and file.size > settings.max_video_size_bytes:
        raise HTTPException(400, f"File too large. Max {settings.MAX_VIDEO_SIZE_MB}MB")

    # ─── Create DB record ─────────────────────────────────────────────────
    video = Video(
        id=uuid.uuid4(),
        owner_id=current_user.id,
        original_filename=file.filename,
        anime_style=anime_style,
        status=VideoStatus.UPLOADING,
    )
    db.add(video)
    await db.flush()

    # ─── Save file ────────────────────────────────────────────────────────
    try:
        path, size = await storage.save_upload(file, video.id)
        video.original_path = path
        video.original_size_bytes = size
        video.status = VideoStatus.UPLOADED

        # Basic size validation post-save
        if size > settings.max_video_size_bytes:
            import os; os.remove(path)
            raise HTTPException(400, f"File too large. Max {settings.MAX_VIDEO_SIZE_MB}MB")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        video.status = VideoStatus.FAILED
        video.error_message = str(e)
        raise HTTPException(500, "Upload failed")

    # ─── Dispatch Celery task ─────────────────────────────────────────────
    try:
        task = convert_video_to_anime.apply_async(
            args=[str(video.id)],
            queue="anime_conversion",
        )
    except Exception as exc:
        logger.error(f"Failed to enqueue conversion task for video {video.id}: {exc}")
        raise HTTPException(status_code=503, detail="Video queue is temporarily unavailable")

    video.celery_task_id = task.id
    video.status = VideoStatus.PROCESSING
    logger.info(f"Dispatched task {task.id} for video {video.id}")

    return video


@router.get("/{video_id}/status", response_model=VideoStatusOut)
async def get_video_status(
    video_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Poll this endpoint to track anime conversion progress (0-100%)."""
    result = await db.execute(
        select(Video).where(Video.id == video_id, Video.owner_id == current_user.id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(404, "Video not found")
    return video


@router.get("/{video_id}", response_model=VideoOut)
async def get_video(
    video_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Video).where(Video.id == video_id, Video.owner_id == current_user.id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(404, "Video not found")
    return video


@router.delete("/{video_id}", status_code=204)
async def delete_video(
    video_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Video).where(Video.id == video_id, Video.owner_id == current_user.id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(404, "Video not found")

    # Delete files
    if video.original_path and not video.original_deleted:
        await storage.delete_original(video.original_path)

    await db.delete(video)
