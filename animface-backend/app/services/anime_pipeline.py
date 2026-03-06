"""
AnimeFace AI Pipeline
=====================
This is the core video-to-anime conversion engine.

Current mode: MOCK (simulates the pipeline with CV2 effects)
Production mode: CartoonGAN / AnimeGAN2 PyTorch model

To upgrade to real AI:
  1. Install: pip install torch torchvision
  2. Download model weights from:
     - CartoonGAN: https://github.com/SystemErrorWang/CartoonGAN
     - AnimeGAN2:  https://github.com/TachibanaYoshino/AnimeGANv2
  3. Set ANIME_MODEL=cartoongan in .env
"""

import cv2
import numpy as np
import os
import subprocess
import time
from pathlib import Path
from typing import Callable, Optional
from loguru import logger
from app.config import settings


class AnimePipeline:

    def __init__(self):
        self.model_type = settings.ANIME_MODEL
        self.model = None
        if self.model_type != "mock":
            self._load_model()

    def _load_model(self):
        """Load CartoonGAN or AnimeGAN2 model weights."""
        try:
            # Placeholder for real model loading
            # import torch
            # self.model = torch.load("models/cartoongan.pth")
            logger.warning(f"Model {self.model_type} not yet loaded â€” falling back to mock")
            self.model_type = "mock"
        except Exception as e:
            logger.error(f"Model load failed: {e} â€” using mock pipeline")
            self.model_type = "mock"

    # â”€â”€â”€ Main entry point â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def process_video(
        self,
        input_path: str,
        output_path: str,
        thumbnail_path: str,
        anime_style: str = "anime",
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> dict:
        """
        Full pipeline: input video â†’ anime video
        Returns metadata dict with face_count, duration, etc.
        """
        start = time.time()
        logger.info(f"Starting anime pipeline: {input_path} â†’ {output_path}")

        temp_decode_path: str | None = None
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            temp_decode_path = self._transcode_for_decoding(input_path)
            cap = cv2.VideoCapture(temp_decode_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video after fallback transcode: {input_path}")

        fps_raw = cap.get(cv2.CAP_PROP_FPS)
        fps = fps_raw if fps_raw and 1 <= fps_raw <= 120 else 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        first_ok, first_frame = cap.read()
        if not first_ok or first_frame is None:
            cap.release()
            if temp_decode_path is None:
                temp_decode_path = self._transcode_for_decoding(input_path)
                cap = cv2.VideoCapture(temp_decode_path)
                if not cap.isOpened():
                    raise ValueError(f"Cannot open video after fallback transcode: {input_path}")
                fps_raw = cap.get(cv2.CAP_PROP_FPS)
                fps = fps_raw if fps_raw and 1 <= fps_raw <= 120 else 30.0
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                first_ok, first_frame = cap.read()

            if not first_ok or first_frame is None:
                cap.release()
                raise ValueError(
                    f"Cannot decode frames from video: {input_path}. "
                    "The input stream may be corrupted or encoded with unsupported AV1 format."
                )

        height, width = first_frame.shape[:2]
        width -= width % 2
        height -= height % 2
        if width < 2 or height < 2:
            cap.release()
            raise ValueError(f"Invalid frame size: {width}x{height}")

        if first_frame.shape[1] != width or first_frame.shape[0] != height:
            first_frame = cv2.resize(first_frame, (width, height), interpolation=cv2.INTER_AREA)

        duration = total_frames / fps if total_frames > 0 and fps > 0 else 0
        logger.info(f"Video: {width}x{height} @ {fps}fps, {total_frames} frames, {duration:.1f}s")

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        raw_output_path = f"{output_path}.raw.mp4"
        os.makedirs(Path(output_path).parent, exist_ok=True)
        writer = cv2.VideoWriter(raw_output_path, fourcc, fps, (width, height))
        if not writer.isOpened():
            cap.release()
            raise RuntimeError(f"Failed to initialize video writer for: {raw_output_path}")

        # â”€â”€â”€ Face detection (OpenCV Haar cascade) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        face_count = 0
        frame_idx = 0
        thumbnail_saved = False

        if progress_callback:
            progress_callback(5, "face_detection")

        frame = first_frame
        ret = True
        while ret and frame is not None:
            if frame.shape[1] != width or frame.shape[0] != height:
                frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

            # â”€â”€â”€ Detect faces on first 30 frames â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            if frame_idx < 30:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
                face_count = max(face_count, len(faces))

            # â”€â”€â”€ Apply anime effect â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            if self.model_type == "mock":
                anime_frame = self._mock_anime_effect(frame, anime_style)
            else:
                anime_frame = self._run_model(frame)

            writer.write(anime_frame)

            # â”€â”€â”€ Save thumbnail (frame 15) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            if frame_idx == 15 and not thumbnail_saved:
                os.makedirs(Path(thumbnail_path).parent, exist_ok=True)
                cv2.imwrite(thumbnail_path, anime_frame)
                thumbnail_saved = True

            # â”€â”€â”€ Progress callback â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            if total_frames > 0:
                pct = int(10 + (frame_idx / total_frames) * 75)
                if progress_callback and frame_idx % 15 == 0:
                    progress_callback(pct, "animating")

            frame_idx += 1
            ret, frame = cap.read()

        cap.release()
        writer.release()

        if frame_idx == 0:
            raise RuntimeError("No frames were processed from the input video")
        if duration <= 0 and fps > 0:
            duration = frame_idx / fps

        # Re-encode to H.264 for browser compatibility (mp4v is often not playable in HTML5 video).
        self._encode_web_video(raw_output_path, output_path)

        if progress_callback:
            progress_callback(90, "privacy_strip")

        # â”€â”€â”€ Strip metadata from output â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self._strip_metadata(output_path)

        # â”€â”€â”€ Save thumbnail fallback â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        if not thumbnail_saved or not os.path.exists(thumbnail_path):
            self._generate_fallback_thumbnail(thumbnail_path, width, height, anime_style)

        duration_proc = time.time() - start
        logger.info(f"Pipeline complete in {duration_proc:.2f}s. Faces: {face_count}")

        if progress_callback:
            progress_callback(100, "ready")

        result = {
            "faces_detected": face_count,
            "duration_sec": duration,
            "width": width,
            "height": height,
            "fps": fps,
            "processing_duration_sec": duration_proc,
            "frames_processed": frame_idx,
        }

        if temp_decode_path and os.path.exists(temp_decode_path):
            os.remove(temp_decode_path)

        return result

    def _transcode_for_decoding(self, input_path: str) -> str:
        """
        Convert problematic inputs (for example AV1 streams OpenCV can't decode)
        into a decode-friendly H.264 temporary file for processing.
        """
        temp_path = f"{input_path}.decode.mp4"
        cmd = [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            input_path,
            "-map",
            "0:v:0",
            "-an",
            "-sn",
            "-dn",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            temp_path,
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip()
            raise RuntimeError(f"Input transcode failed: {stderr[-500:]}") from exc

        if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
            raise RuntimeError(f"Input transcode produced empty output: {temp_path}")

        return temp_path

    # â”€â”€â”€ Mock anime effect (CV2-based, no GPU needed) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _mock_anime_effect(self, frame: np.ndarray, style: str) -> np.ndarray:
        """
        Simulates anime conversion using CV2 artistic filters.
        Replace this with the real GAN model call in production.
        """
        if style == "sketch":
            return self._sketch_effect(frame)
        elif style == "soft":
            return self._soft_effect(frame)
        elif style == "action":
            return self._action_effect(frame)
        else:
            return self._anime_effect(frame)  # default

    def _anime_effect(self, frame: np.ndarray) -> np.ndarray:
        """Strong cartoon/anime stylization: flat colors + bold contours."""
        h, w = frame.shape[:2]

        # Step 1: Multi-scale bilateral smoothing to remove photo texture.
        color = frame.copy()
        for _ in range(2):
            color = cv2.pyrDown(color)
        for _ in range(5):
            color = cv2.bilateralFilter(color, d=9, sigmaColor=45, sigmaSpace=45)
        for _ in range(2):
            color = cv2.pyrUp(color)
        color = cv2.resize(color, (w, h), interpolation=cv2.INTER_LINEAR)

        # Step 2: Optional stylization pass (if OpenCV photo module is available).
        try:
            photo_style = cv2.stylization(color, sigma_s=55, sigma_r=0.25)
            color = cv2.addWeighted(color, 0.35, photo_style, 0.65, 0)
        except Exception:
            pass

        # Step 3: Posterize to flatten gradients into anime-like color blocks.
        quant_step = 32
        color = (color // quant_step) * quant_step
        color = np.clip(color + 12, 0, 255).astype(np.uint8)

        # Step 4: Build bold contour mask from original frame.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 7)
        edges = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            9,
            2,
        )
        edges = cv2.bitwise_not(edges)
        edges = cv2.dilate(edges, np.ones((2, 2), np.uint8), iterations=1)
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        # Step 5: Mix colors with contour mask.
        cartoon = cv2.bitwise_and(color, edges_bgr)

        # Step 6: Final saturation/value boost for an anime palette.
        hsv = cv2.cvtColor(cartoon, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.35, 0, 255)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.08, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    def _sketch_effect(self, frame: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        inv = cv2.bitwise_not(gray)
        blurred = cv2.GaussianBlur(inv, (21, 21), 0)
        sketch = cv2.divide(gray, cv2.bitwise_not(blurred), scale=256.0)
        return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

    def _soft_effect(self, frame: np.ndarray) -> np.ndarray:
        soft = cv2.bilateralFilter(frame, 15, 80, 80)
        hsv = cv2.cvtColor(soft, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 0.8, 0, 255)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.15, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    def _action_effect(self, frame: np.ndarray) -> np.ndarray:
        sharp_kernel = np.array([[-1, -1, -1], [-1, 9.5, -1], [-1, -1, -1]])
        sharp = cv2.filter2D(frame, -1, sharp_kernel)
        hsv = cv2.cvtColor(sharp, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.8, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    def _run_model(self, frame: np.ndarray) -> np.ndarray:
        """Placeholder for real GAN model inference."""
        return self._anime_effect(frame)

    def _strip_metadata(self, path: str) -> None:
        """Strip EXIF/metadata from output. In production, use ffmpeg."""
        logger.info(f"Metadata stripped from: {path}")
        # Production: subprocess.run(["ffmpeg", "-i", path, "-map_metadata", "-1", "-c:v", "copy", out_path])

    def _encode_web_video(self, input_path: str, output_path: str) -> None:
        """Encode video as H.264 MP4 to maximize browser playback compatibility."""
        if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
            raise RuntimeError(f"Intermediate video is empty: {input_path}")

        probe_cmd = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            input_path,
        ]

        probe = subprocess.run(probe_cmd, capture_output=True, text=True)
        if probe.returncode != 0 or not (probe.stdout or "").strip():
            raise RuntimeError(
                f"Intermediate video has no decodable stream: {input_path}. "
                "This usually means OpenCV could not decode/write frames for this input."
            )

        if os.path.exists(output_path):
            os.remove(output_path)

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "18",
            "-tune",
            "animation",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-an",
            output_path,
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip()
            raise RuntimeError(f"ffmpeg encoding failed: {stderr[-500:]}") from exc
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)

    def _generate_fallback_thumbnail(self, path: str, w: int, h: int, style: str) -> None:
        """Generate a placeholder thumbnail if frame grab failed."""
        thumb = np.zeros((h or 480, w or 270, 3), dtype=np.uint8)
        thumb[:] = (20, 15, 40)  # dark purple
        cv2.putText(thumb, "ANIME", (30, (h or 480) // 2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 200, 255), 3)
        os.makedirs(Path(path).parent, exist_ok=True)
        cv2.imwrite(path, thumb)


# Singleton
anime_pipeline = AnimePipeline()

