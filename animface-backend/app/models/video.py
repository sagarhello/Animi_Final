import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum


class VideoStatus(str, enum.Enum):
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"     # Celery picked it up
    FACE_DETECTION = "face_detection"
    ANIMATING = "animating"
    PRIVACY_STRIP = "privacy_strip"
    READY = "ready"
    FAILED = "failed"


class AnimeStyle(str, enum.Enum):
    ANIME = "anime"
    SKETCH = "sketch"
    SOFT = "soft"
    ACTION = "action"


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # ─── Original file (temporary — deleted after animation) ──
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    original_path: Mapped[str | None] = mapped_column(String(500), nullable=True)    # local path or S3 key
    original_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    original_duration_sec: Mapped[float | None] = mapped_column(Float, nullable=True)
    original_deleted: Mapped[bool] = mapped_column(default=False)  # GDPR compliance

    # ─── Animated output ──────────────────────────────────────
    animated_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    animated_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    thumbnail_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    anime_style: Mapped[AnimeStyle] = mapped_column(SAEnum(AnimeStyle), default=AnimeStyle.ANIME)

    # ─── Processing metadata ──────────────────────────────────
    status: Mapped[VideoStatus] = mapped_column(SAEnum(VideoStatus), default=VideoStatus.UPLOADING, index=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    processing_progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    faces_detected: Mapped[int] = mapped_column(Integer, default=0)
    processing_duration_sec: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ─── Video metadata (sanitized) ──────────────────────────
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fps: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ─── Timestamps ──────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processing_started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    processing_completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # ─── Relationships ────────────────────────────────────────
    owner: Mapped["User"] = relationship("User", back_populates="videos")
    post: Mapped["Post | None"] = relationship("Post", back_populates="video", uselist=False)

    def __repr__(self) -> str:
        return f"<Video {self.id} status={self.status}>"
