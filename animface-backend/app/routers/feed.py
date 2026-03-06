import base64
import json
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.user import User
from app.models.post import Post
from app.models.social import Follow
from app.schemas.post import FeedResponse, PostOut
from app.core.dependencies import get_current_user, get_current_user_optional

router = APIRouter(prefix="/feed", tags=["Feed"])

PAGE_SIZE = 10


def encode_cursor(post_id: str, created_at: datetime) -> str:
    data = {"id": post_id, "ts": created_at.isoformat()}
    return base64.b64encode(json.dumps(data).encode()).decode()


def decode_cursor(cursor: str) -> dict | None:
    try:
        return json.loads(base64.b64decode(cursor).decode())
    except Exception:
        return None


@router.get("/", response_model=FeedResponse)
async def get_feed(
    cursor: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cursor-based paginated feed.
    Returns posts from users you follow + your own posts, newest first.
    """
    # Get following IDs
    follow_result = await db.execute(
        select(Follow.following_id).where(Follow.follower_id == current_user.id)
    )
    following_ids = [r[0] for r in follow_result.all()]
    feed_user_ids = following_ids + [current_user.id]

    # Build query
    query = (
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.video), selectinload(Post.likes))
        .where(Post.author_id.in_(feed_user_ids), Post.is_public == True, Post.is_archived == False)  # noqa
        .order_by(Post.created_at.desc())
        .limit(PAGE_SIZE + 1)
    )

    # Apply cursor
    if cursor:
        cursor_data = decode_cursor(cursor)
        if cursor_data:
            query = query.where(Post.created_at < datetime.fromisoformat(cursor_data["ts"]))

    result = await db.execute(query)
    posts = result.scalars().all()

    has_more = len(posts) > PAGE_SIZE
    if has_more:
        posts = posts[:PAGE_SIZE]

    next_cursor = None
    if has_more and posts:
        last = posts[-1]
        next_cursor = encode_cursor(str(last.id), last.created_at)

    post_outs = [
        PostOut(
            **{
                "id": p.id, "caption": p.caption, "like_count": p.like_count,
                "comment_count": p.comment_count, "view_count": p.view_count,
                "is_public": p.is_public, "comments_enabled": p.comments_enabled,
                "created_at": p.created_at, "author": p.author, "video": p.video,
                "is_liked": any(like.user_id == current_user.id for like in p.likes),
            }
        )
        for p in posts
    ]

    return FeedResponse(posts=post_outs, next_cursor=next_cursor, has_more=has_more)


@router.get("/explore", response_model=FeedResponse)
async def explore_feed(
    cursor: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Public explore feed — most recent public posts from all users."""
    query = (
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.video), selectinload(Post.likes))
        .where(Post.is_public == True, Post.is_archived == False)  # noqa
        .order_by(Post.created_at.desc())
        .limit(PAGE_SIZE + 1)
    )

    if cursor:
        cursor_data = decode_cursor(cursor)
        if cursor_data:
            query = query.where(Post.created_at < datetime.fromisoformat(cursor_data["ts"]))

    result = await db.execute(query)
    posts = result.scalars().all()

    has_more = len(posts) > PAGE_SIZE
    if has_more:
        posts = posts[:PAGE_SIZE]

    next_cursor = None
    if has_more and posts:
        last = posts[-1]
        next_cursor = encode_cursor(str(last.id), last.created_at)

    uid = current_user.id if current_user else None
    post_outs = [
        PostOut(
            **{
                "id": p.id, "caption": p.caption, "like_count": p.like_count,
                "comment_count": p.comment_count, "view_count": p.view_count,
                "is_public": p.is_public, "comments_enabled": p.comments_enabled,
                "created_at": p.created_at, "author": p.author, "video": p.video,
                "is_liked": uid is not None and any(like.user_id == uid for like in p.likes),
            }
        )
        for p in posts
    ]

    return FeedResponse(posts=post_outs, next_cursor=next_cursor, has_more=has_more)
