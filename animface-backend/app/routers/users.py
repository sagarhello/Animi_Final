import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.user import User
from app.models.post import Post
from app.models.social import Follow
from app.schemas.user import UserOut, UserProfile, UserUpdate
from app.schemas.post import PostOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await _build_profile(db, current_user, current_user.id)


@router.patch("/me", response_model=UserOut)
async def update_profile(
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    return current_user


@router.get("/@{username}", response_model=UserProfile)
async def get_user_profile(
    username: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.username == username.lower()))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(404, "User not found")
    return await _build_profile(db, user, current_user.id)


async def _build_profile(db: AsyncSession, user: User, viewer_id: uuid.UUID) -> UserProfile:
    follower_count = await db.scalar(select(func.count()).where(Follow.following_id == user.id)) or 0
    following_count = await db.scalar(select(func.count()).where(Follow.follower_id == user.id)) or 0
    post_count = await db.scalar(select(func.count()).where(Post.author_id == user.id, Post.is_archived == False)) or 0  # noqa

    return UserProfile(
        id=user.id, username=user.username, display_name=user.display_name,
        avatar_emoji=user.avatar_emoji, anime_style=user.anime_style,
        is_verified=user.is_verified, created_at=user.created_at,
        bio=user.bio, profile_private=user.profile_private,
        follower_count=follower_count, following_count=following_count, post_count=post_count,
    )


# ─── FOLLOW / UNFOLLOW ─────────────────────────────────────────────────────
@router.post("/@{username}/follow", status_code=200)
async def toggle_follow(
    username: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.username == username.lower()))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(404, "User not found")
    if target.id == current_user.id:
        raise HTTPException(400, "Cannot follow yourself")

    follow_result = await db.execute(
        select(Follow).where(Follow.follower_id == current_user.id, Follow.following_id == target.id)
    )
    existing = follow_result.scalar_one_or_none()

    if existing:
        await db.delete(existing)
        return {"following": False, "username": username}
    else:
        follow = Follow(id=uuid.uuid4(), follower_id=current_user.id, following_id=target.id)
        db.add(follow)
        return {"following": True, "username": username}


@router.get("/@{username}/posts", response_model=list[PostOut])
async def get_user_posts(
    username: str,
    limit: int = Query(12, le=30),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.username == username.lower()))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    posts_result = await db.execute(
        select(Post)
        .options(
            selectinload(Post.author), selectinload(Post.video), selectinload(Post.likes)
        )
        .where(Post.author_id == user.id, Post.is_public == True, Post.is_archived == False)  # noqa
        .order_by(Post.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    posts = posts_result.scalars().all()

    return [
        PostOut(**{
            "id": p.id, "caption": p.caption, "like_count": p.like_count,
            "comment_count": p.comment_count, "view_count": p.view_count,
            "is_public": p.is_public, "comments_enabled": p.comments_enabled,
            "created_at": p.created_at, "author": p.author, "video": p.video,
            "is_liked": any(like.user_id == current_user.id for like in p.likes),
        })
        for p in posts
    ]
