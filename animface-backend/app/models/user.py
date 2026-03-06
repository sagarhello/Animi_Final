import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # ─── Identity (all anonymous-first) ──────────────────
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # ─── Profile ───────────────────────────────────────────
    display_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Emoji avatar — no real photo ever stored
    avatar_emoji: Mapped[str] = mapped_column(String(10), default="👾")
    anime_style: Mapped[str] = mapped_column(String(20), default="anime")  # anime | sketch | soft

    # ─── Status ────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)

    # ─── Privacy flags ─────────────────────────────────────
    profile_private: Mapped[bool] = mapped_column(Boolean, default=False)

    # ─── Timestamps ────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # ─── Relationships ─────────────────────────────────────
    videos: Mapped[list["Video"]] = relationship("Video", back_populates="owner", cascade="all, delete-orphan")  # noqa
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author", cascade="all, delete-orphan")  # noqa
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="user", cascade="all, delete-orphan")  # noqa
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="author", cascade="all, delete-orphan")  # noqa
    followers: Mapped[list["Follow"]] = relationship("Follow", foreign_keys="Follow.following_id", back_populates="following")  # noqa
    following: Mapped[list["Follow"]] = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower")  # noqa
    stories: Mapped[list["Story"]] = relationship("Story", back_populates="author", cascade="all, delete-orphan")  # noqa

    def __repr__(self) -> str:
        return f"<User {self.username}>"
