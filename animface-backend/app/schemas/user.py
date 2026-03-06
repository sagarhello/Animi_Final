import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    display_name: Optional[str]
    avatar_emoji: str
    anime_style: str
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfile(UserOut):
    bio: Optional[str]
    profile_private: bool
    follower_count: int = 0
    following_count: int = 0
    post_count: int = 0


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_emoji: Optional[str] = None
    anime_style: Optional[str] = None
    profile_private: Optional[bool] = None
