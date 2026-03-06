# 🎌 AnimeFace Backend

**Privacy-first anime social platform API**  
Upload video → Auto anime conversion → No real face ever stored

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI (Python 3.11) |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Task Queue | Celery + Redis |
| AI Pipeline | OpenCV (mock) → CartoonGAN (production) |
| Auth | JWT (access + refresh tokens) |
| Storage | Local filesystem → AWS S3 ready |

---

## 🚀 Quick Start (Docker)

```bash
# 1. Clone and configure
cp .env.example .env

# 2. Start everything
docker-compose up -d

# 3. API is live at:
open http://localhost:8000/docs

# 4. Monitor Celery workers at:
open http://localhost:5555
```

---

## 🔧 Local Development (no Docker)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL connection string

# 4. Start PostgreSQL and Redis locally, then run migrations
alembic upgrade head

# 5. Start the API
uvicorn app.main:app --reload --port 8000

# 6. Start Celery worker (separate terminal)
celery -A app.workers.celery_app worker --loglevel=info -Q anime_conversion
```

---

## 📡 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login, get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user |

### Videos (Core Feature)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/videos/upload` | Upload video → triggers anime conversion |
| GET | `/api/v1/videos/{id}/status` | **Poll for conversion progress** (0-100%) |
| GET | `/api/v1/videos/{id}` | Get video details |
| DELETE | `/api/v1/videos/{id}` | Delete video |

### Posts
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/posts/` | Publish animated video as post |
| GET | `/api/v1/posts/{id}` | Get post |
| DELETE | `/api/v1/posts/{id}` | Delete post |
| POST | `/api/v1/posts/{id}/like` | Toggle like |
| GET | `/api/v1/posts/{id}/comments` | Get comments |
| POST | `/api/v1/posts/{id}/comments` | Add comment |

### Feed
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/feed/` | Personal feed (following) |
| GET | `/api/v1/feed/explore` | Public explore feed |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | My profile |
| PATCH | `/api/v1/users/me` | Update profile |
| GET | `/api/v1/users/@{username}` | View user profile |
| POST | `/api/v1/users/@{username}/follow` | Follow/unfollow |
| GET | `/api/v1/users/@{username}/posts` | User's posts |

### Stories (24hr)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/stories/` | Post a story |
| GET | `/api/v1/stories/following` | Stories from following |
| POST | `/api/v1/stories/{id}/view` | Mark story as viewed |

---

## 🔄 Video Upload Flow

```
Frontend                    API                  Celery Worker
    |                        |                        |
    |-- POST /videos/upload ->|                        |
    |                        |-- save file            |
    |                        |-- create DB record     |
    |                        |-- dispatch task ------>|
    |<-- {id, status: proc} -|                        |
    |                        |                   face detection
    |-- GET /videos/{id}/status (poll every 2s)  animating
    |<-- {progress: 45%} ----|                        |
    |-- GET /videos/{id}/status                  privacy strip
    |<-- {status: ready, animated_path: ...}          |
    |                        |<-- original deleted    |
    |-- POST /posts/ ------->|                        |
    |<-- post published -----|                        |
```

---

## 🔒 Privacy Guarantees

1. **On-device validation** — File type/size checked before upload
2. **Original deleted** — Source video deleted within 60s of animation completing
3. **No face storage** — Face detection runs only to count faces, no data persisted
4. **Metadata stripped** — EXIF/location data removed from output
5. **Anonymous accounts** — No real name, phone, or PII required to register

---

## 🤖 Upgrading to Real AI Model

Current: OpenCV-based cartoon filter (no GPU needed)

To use CartoonGAN:
```bash
# Install PyTorch
pip install torch torchvision

# Download weights
wget https://github.com/SystemErrorWang/CartoonGAN/releases/...

# Update .env
ANIME_MODEL=cartoongan
```

To use AnimeGANv2:
```bash
ANIME_MODEL=animegan2
```

The `anime_pipeline.py` `_run_model()` method is the only place that needs updating.

---

## 📊 Monitoring

- **API docs**: http://localhost:8000/docs  
- **Celery tasks**: http://localhost:5555 (Flower)  
- **Health check**: http://localhost:8000/health  

---

## 🗺️ Next Steps (Phase 2)

- [ ] WebSocket for real-time conversion progress  
- [ ] Voice morphing (librosa + pitch shift)  
- [ ] Multiple anime style models  
- [ ] Rate limiting per user  
- [ ] S3 storage migration  
- [ ] Admin dashboard  
