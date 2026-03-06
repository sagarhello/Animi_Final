import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.user import User
from app.models.video import Video, VideoStatus
from app.models.social import Story, Follow
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/stories", tags=["Stories"])


@router.post("/", status_code=201)
async def create_story(
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
    if video.status != VideoStatus.READY:
        raise HTTPException(400, "Video is not ready")

    story = Story(
        id=uuid.uuid4(),
        author_id=current_user.id,
        video_id=video_id,
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    db.add(story)
    return {"id": story.id, "expires_at": story.expires_at}


@router.get("/following")
async def get_following_stories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get active stories from people you follow."""
    follow_result = await db.execute(
        select(Follow.following_id).where(Follow.follower_id == current_user.id)
    )
    following_ids = [r[0] for r in follow_result.all()]

    now = datetime.utcnow()
    result = await db.execute(
        select(Story)
        .options(selectinload(Story.author), selectinload(Story.video))
        .where(
            Story.author_id.in_(following_ids),
            Story.expires_at > now,
            Story.is_active == True,  # noqa
        )
        .order_by(Story.created_at.desc())
    )
    stories = result.scalars().all()

    return [
        {
            "id": s.id,
            "author": {"username": s.author.username, "avatar_emoji": s.author.avatar_emoji},
            "video_url": s.video.animated_path,
            "thumbnail_url": s.video.thumbnail_path,
            "view_count": s.view_count,
            "expires_at": s.expires_at,
            "created_at": s.created_at,
        }
        for s in stories
    ]


@router.post("/{story_id}/view", status_code=200)
async def view_story(
    story_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Story).where(Story.id == story_id))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(404, "Story not found")

    story.view_count += 1
    return {"view_count": story.view_count}
