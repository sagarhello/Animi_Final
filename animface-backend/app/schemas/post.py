import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from app.schemas.user import UserOut
from app.schemas.video import VideoOut


class PostCreate(BaseModel):
    video_id: uuid.UUID
    caption: Optional[str] = None
    is_public: bool = True
    comments_enabled: bool = True


class PostOut(BaseModel):
    id: uuid.UUID
    caption: Optional[str]
    like_count: int
    comment_count: int
    view_count: int
    is_public: bool
    comments_enabled: bool
    created_at: datetime
    author: UserOut
    video: VideoOut
    is_liked: bool = False  # populated per-request

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[uuid.UUID] = None


class CommentOut(BaseModel):
    id: uuid.UUID
    content: str
    like_count: int
    created_at: datetime
    author: UserOut
    reply_count: int = 0

    model_config = {"from_attributes": True}


class FeedResponse(BaseModel):
    posts: List[PostOut]
    next_cursor: Optional[str]
    has_more: bool
