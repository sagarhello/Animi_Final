from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pathlib import Path
from loguru import logger
import time

from app.config import settings
from app.database import init_db
from app.routers import auth, videos, posts, feed, users, stories


# ─── Lifespan ────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 AnimeFace API starting up...")
    await init_db()
    logger.info("✅ Database tables initialized")
    yield
    logger.info("👋 AnimeFace API shutting down")


# ─── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AnimeFace API",
    description="""
## 🎌 AnimeFace — Privacy-First Anime Social Platform

Upload your video → **automatically converted to anime** → no real face ever exposed.

### Key Features
- 🔒 **Privacy-first**: Original videos deleted after conversion
- 🤖 **Auto anime conversion**: No avatar selection needed
- 🎭 **Multiple styles**: Anime, Sketch, Soft, Action
- ⚡ **Real-time progress**: WebSocket-compatible polling
- 👥 **Full social layer**: Feed, likes, comments, follows, stories

### Authentication
All protected endpoints require `Authorization: Bearer <token>`.
Get a token via `/auth/login` or `/auth/register`.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ─── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request timing middleware ────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    response.headers["X-Process-Time"] = f"{duration:.3f}s"
    return response


# ─── Static files (serve animated videos locally) ────────────────────────────
uploads_path = Path(settings.LOCAL_UPLOAD_DIR)
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=str(uploads_path)), name="static")


# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/v1")
app.include_router(videos.router, prefix="/api/v1")
app.include_router(posts.router, prefix="/api/v1")
app.include_router(feed.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(stories.router, prefix="/api/v1")


# ─── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "env": settings.APP_ENV,
        "anime_model": settings.ANIME_MODEL,
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "name": "AnimeFace API",
        "docs": "/docs",
        "version": "1.0.0",
        "privacy": "Original videos are deleted immediately after anime conversion. No real faces stored.",
    }
