import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.user import User
from app.models.video import Video, VideoStatus
from app.models.post import Post
from app.models.social import Like, Comment
from app.schemas.post import PostCreate, PostOut, CommentCreate, CommentOut
from app.core.dependencies import get_current_user, get_current_user_optional

router = APIRouter(prefix="/posts", tags=["Posts"])


def _build_post_out(post: Post, current_user_id: uuid.UUID | None = None) -> dict:
    """Serialize post with is_liked populated."""
    data = {
        "id": post.id,
        "caption": post.caption,
        "like_count": post.like_count,
        "comment_count": post.comment_count,
        "view_count": post.view_count,
        "is_public": post.is_public,
        "comments_enabled": post.comments_enabled,
        "created_at": post.created_at,
        "author": post.author,
        "video": post.video,
        "is_liked": False,
    }
    if current_user_id:
        data["is_liked"] = any(like.user_id == current_user_id for like in post.likes)
    return data


@router.post("/", response_model=PostOut, status_code=201)
async def create_post(
    body: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate video belongs to user and is ready
    result = await db.execute(
        select(Video).where(
            Video.id == body.video_id,
            Video.owner_id == current_user.id,
        )
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(404, "Video not found")
    if video.status != VideoStatus.READY:
        raise HTTPException(400, f"Video is not ready yet. Status: {video.status}")

    existing_post_result = await db.execute(select(Post.id).where(Post.video_id == body.video_id))
    if existing_post_result.scalar_one_or_none():
        raise HTTPException(409, "Video is already published as a post")

    post = Post(
        id=uuid.uuid4(),
        author_id=current_user.id,
        video_id=body.video_id,
        caption=body.caption,
        is_public=body.is_public,
        comments_enabled=body.comments_enabled,
    )
    db.add(post)
    await db.flush()

    # Reload with relationships
    result = await db.execute(
        select(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.video),
            selectinload(Post.likes),
        )
        .where(Post.id == post.id)
    )
    post = result.scalar_one()
    return PostOut(**_build_post_out(post, current_user.id))


@router.get("/{post_id}", response_model=PostOut)
async def get_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.video), selectinload(Post.likes))
        .where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post or not post.is_public:
        raise HTTPException(404, "Post not found")

    # Increment view count
    post.view_count += 1

    uid = current_user.id if current_user else None
    return PostOut(**_build_post_out(post, uid))


@router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.author_id == current_user.id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Post not found")
    await db.delete(post)


# ─── LIKES ─────────────────────────────────────────────────────────────────
@router.post("/{post_id}/like", status_code=200)
async def toggle_like(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get post
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Post not found")

    # Check existing like
    like_result = await db.execute(
        select(Like).where(Like.user_id == current_user.id, Like.post_id == post_id)
    )
    existing = like_result.scalar_one_or_none()

    if existing:
        await db.delete(existing)
        post.like_count = max(0, post.like_count - 1)
        return {"liked": False, "like_count": post.like_count}
    else:
        like = Like(id=uuid.uuid4(), user_id=current_user.id, post_id=post_id)
        db.add(like)
        post.like_count += 1
        return {"liked": True, "like_count": post.like_count}


# ─── COMMENTS ──────────────────────────────────────────────────────────────
@router.get("/{post_id}/comments", response_model=list[CommentOut])
async def get_comments(
    post_id: uuid.UUID,
    limit: int = Query(20, le=50),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.author), selectinload(Comment.replies))
        .where(Comment.post_id == post_id, Comment.parent_id == None, Comment.is_deleted == False)  # noqa
        .order_by(Comment.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    comments = result.scalars().all()
    return [
        CommentOut(
            id=c.id, content=c.content, like_count=c.like_count,
            created_at=c.created_at, author=c.author, reply_count=len(c.replies)
        )
        for c in comments
    ]


@router.post("/{post_id}/comments", response_model=CommentOut, status_code=201)
async def add_comment(
    post_id: uuid.UUID,
    body: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Post not found")
    if not post.comments_enabled:
        raise HTTPException(403, "Comments disabled on this post")

    content = body.content.strip()
    if not content:
        raise HTTPException(400, "Comment cannot be empty")

    comment = Comment(
        id=uuid.uuid4(),
        author_id=current_user.id,
        post_id=post_id,
        content=content,
        parent_id=body.parent_id,
    )
    db.add(comment)
    post.comment_count += 1
    await db.flush()

    return CommentOut(
        id=comment.id, content=comment.content, like_count=0,
        created_at=comment.created_at, author=current_user, reply_count=0
    )


@router.delete("/{post_id}/comments/{comment_id}", status_code=204)
async def delete_comment(
    post_id: uuid.UUID,
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Comment).where(
            Comment.id == comment_id,
            Comment.post_id == post_id,
            Comment.author_id == current_user.id,
        )
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(404, "Comment not found")

    comment.is_deleted = True
    comment.content = "[deleted]"
