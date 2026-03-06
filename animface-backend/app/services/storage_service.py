import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile
from app.config import settings
from loguru import logger


class StorageService:
    """Handles file storage. Local now, S3-ready for cloud migration."""

    def __init__(self):
        self.backend = settings.STORAGE_BACKEND
        self.base_dir = Path(settings.LOCAL_UPLOAD_DIR)
        self._ensure_dirs()

    def _ensure_dirs(self):
        (self.base_dir / "originals").mkdir(parents=True, exist_ok=True)
        (self.base_dir / "animated").mkdir(parents=True, exist_ok=True)
        (self.base_dir / "thumbnails").mkdir(parents=True, exist_ok=True)

    # ─── Upload ──────────────────────────────────────────────────────────────
    async def save_upload(self, file: UploadFile, video_id: uuid.UUID) -> tuple[str, int]:
        """Save uploaded video. Returns (path, size_bytes)."""
        ext = Path(file.filename).suffix.lower() if file.filename else ".mp4"
        filename = f"{video_id}{ext}"
        path = self.base_dir / "originals" / filename

        total = 0
        async with aiofiles.open(path, "wb") as f:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                await f.write(chunk)
                total += len(chunk)

        logger.info(f"Saved upload: {path} ({total} bytes)")
        return str(path), total

    # ─── Animated output ─────────────────────────────────────────────────────
    def get_animated_path(self, video_id: uuid.UUID) -> str:
        return str(self.base_dir / "animated" / f"{video_id}_anime.mp4")

    def get_thumbnail_path(self, video_id: uuid.UUID) -> str:
        return str(self.base_dir / "thumbnails" / f"{video_id}_thumb.jpg")

    # ─── Delete original (privacy) ───────────────────────────────────────────
    async def delete_original(self, path: str) -> bool:
        try:
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"Deleted original: {path}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete original {path}: {e}")
        return False

    # ─── Public URL ──────────────────────────────────────────────────────────
    def get_public_url(self, path: str) -> str:
        """Convert local path to URL. In production, return CDN URL."""
        if self.backend == "local":
            normalized = Path(path).as_posix().replace("\\", "/")
            marker = f"/{self.base_dir.name}/"

            if marker in normalized:
                suffix = normalized.split(marker, 1)[1].lstrip("/")
                normalized = f"{self.base_dir.name}/{suffix}"
            else:
                normalized = normalized.lstrip("./")
                if not normalized.startswith(f"{self.base_dir.name}/"):
                    normalized = f"{self.base_dir.name}/{normalized.lstrip('/')}"

            return f"/static/{normalized}"
        # TODO: return f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{path}"
        return path

    # ─── Validate video ──────────────────────────────────────────────────────
    @staticmethod
    def validate_video_file(file: UploadFile) -> None:
        allowed_types = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/webm", "video/avi"}
        allowed_exts = {".mp4", ".mov", ".avi", ".webm"}

        content_type = file.content_type or ""
        if content_type not in allowed_types:
            from fastapi import HTTPException
            raise HTTPException(400, f"Invalid file type: {content_type}. Allowed: mp4, mov, avi, webm")

        if file.filename:
            ext = Path(file.filename).suffix.lower()
            if ext not in allowed_exts:
                from fastapi import HTTPException
                raise HTTPException(400, f"Invalid extension: {ext}")


storage = StorageService()
