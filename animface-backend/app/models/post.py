import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, unique=True)

    # ─── Content ──────────────────────────────────────────────
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ─── Counts (denormalized for perf) ──────────────────────
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    share_count: Mapped[int] = mapped_column(Integer, default=0)

    # ─── Settings ─────────────────────────────────────────────
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    comments_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    # ─── Timestamps ───────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ─── Relationships ────────────────────────────────────────
    author: Mapped["User"] = relationship("User", back_populates="posts")
    video: Mapped["Video"] = relationship("Video", back_populates="post")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post", cascade="all, delete-orphan", order_by="Comment.created_at")

    def __repr__(self) -> str:
        return f"<Post {self.id}>"
