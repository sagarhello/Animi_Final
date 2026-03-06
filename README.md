# Animi Final

AnimeFace social app:
- Frontend: React + Vite
- Backend: FastAPI + Celery + Redis + PostgreSQL

## Public Deployment

### 1. Backend on Render

This repo includes `render.yaml`, so Render can provision:
- PostgreSQL (`animi-db`)
- Redis (`animi-redis`)
- Web service (`animi-api`) that runs API + Celery worker

Steps:
1. Go to Render Dashboard -> New -> Blueprint.
2. Connect this GitHub repo: `sagarhello/Animi_Final`.
3. Deploy the blueprint.
4. After deploy, open `animi-api` service -> Environment.
5. Set `ALLOWED_ORIGINS` to your frontend domain.
   Example:
   - `http://localhost:5173,https://your-frontend-domain.vercel.app`

Important:
- Current storage backend is local (`uploads/`), suitable for demos.
- For production durability, migrate video storage to S3/R2.

### 2. Frontend on Vercel

Steps:
1. Import `animface-frontend-clean` as a project in Vercel.
2. Build settings:
   - Build command: `npm run build`
   - Output directory: `dist`
3. Add env var in Vercel:
   - `VITE_API_BASE_URL=https://<your-render-api-domain>`
4. Deploy.

### 3. Final CORS check

After frontend deploy, update Render:
- `ALLOWED_ORIGINS=https://<your-vercel-domain>`

Then test:
- Register/login
- Upload and convert video
- Publish post
- Play video in feed
