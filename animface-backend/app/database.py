from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine
from app.config import settings


# ─── Async engine (for FastAPI routes) ───────────────────────────────────────
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# ─── Sync engine (for Alembic migrations) ────────────────────────────────────
sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)


# ─── Base model class ─────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ─── Dependency ──────────────────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ─── Init tables (dev only — use Alembic in production) ──────────────────────
async def init_db():
    async with async_engine.begin() as conn:
        from app.models import user, video, post, social  # noqa: import all models
        await conn.run_sync(Base.metadata.create_all)
