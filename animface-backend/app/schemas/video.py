import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from app.models.video import VideoStatus, AnimeStyle


class VideoOut(BaseModel):
    id: uuid.UUID
    status: VideoStatus
    anime_style: AnimeStyle
    animated_path: Optional[str]
    thumbnail_path: Optional[str]
    processing_progress: int
    faces_detected: int
    original_duration_sec: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


class VideoStatusOut(BaseModel):
    id: uuid.UUID
    status: VideoStatus
    processing_progress: int
    error_message: Optional[str]
    animated_path: Optional[str]
    thumbnail_path: Optional[str]
    faces_detected: int

    model_config = {"from_attributes": True}
