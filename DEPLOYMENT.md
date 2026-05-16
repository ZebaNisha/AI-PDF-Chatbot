# 🚀 Ultimate Zero-Cost Deployment Guide
---

## 1. The "Free Five" Service Setup

| Service | Provider | What it hosts |
| :--- | :--- | :--- |
| **Frontend** | [Vercel](https://vercel.com/) | Next.js Website |
| **Database** | [Supabase](https://supabase.com/) | PostgreSQL (User accounts & Metadata) |
| **Vector DB** | [Qdrant Cloud](https://cloud.qdrant.io/) | Semantic Vector Search (PDF chunks) |
| **Redis** | [Upstash](https://upstash.com/) | Celery Broker (Task queue) |
| **Backend** | [Render](https://render.com/) | FastAPI + Celery Worker (Combined) |

---

## 2. Step-by-Step Instructions

### Step A: Database (Supabase)
1. Create a project on Supabase.
2. Go to **Project Settings > Database**.
3. Copy the **URI** string (use the one ending in `5432`). It looks like: `postgresql://postgres:[PASSWORD]@db.xxxx.supabase.co:5432/postgres`
4. **Important:** Add `+asyncpg` after `postgresql`, so it becomes: `postgresql+asyncpg://...`

### Step B: Vector DB (Qdrant)
1. Create a "Free Tier" cluster on Qdrant Cloud.
2. Copy the **Endpoint URL** and generate an **API Key**.

### Step C: Redis (Upstash)
1. Create a Redis database on Upstash.
2. Copy the **Rediss URL** (starts with `rediss://`).

### Step D: Backend (Render)
1. Create a **New Web Service** on Render.
2. Connect your GitHub repo.
3. Set **Root Directory** to `backend`.
4. Set **Environment Variables**:
   - `DATABASE_URL`: (From Step A)
   - `QDRANT_URL`: (From Step B)
   - `QDRANT_API_KEY`: (From Step B)
   - `REDIS_URL`: (From Step C)
   - `GROQ_API_KEY`: (Your Groq Key)
   - `CORS_ORIGINS`: `["*"]` (Or your Vercel URL once deployed)

### Step E: Frontend (Vercel)
1. Create a new project on Vercel.
2. Connect your GitHub repo.
3. Set **Root Directory** to `frontend`.
4. Set **Environment Variables**:
   - `NEXT_PUBLIC_API_URL`: The URL Render gave you (e.g., `https://pdf-backend.onrender.com`)

---

## 3. Why this works for free?
- **Combined Backend:** I updated your `Dockerfile` and added `supervisord.conf`. This allows Render to run your **FastAPI server** and **Celery worker** in the same free container. Usually, you'd need two paid services for this!
- **Serverless Redis:** Upstash Redis is "pay-as-you-go" but has a permanent free tier that won't charge you for low usage.
- **Auto-Sleep:** Render's free tier sleeps after 15 minutes of inactivity. The first request might take 30 seconds to wake up, but after that, it's fast!

---

## 4. Final Push
Once you've saved these files, run:
```bash
git add .
git commit -m "chore: prepare for production deployment with supervisor"
git push origin main
```
Then go to Render/Vercel and start the deployment!
