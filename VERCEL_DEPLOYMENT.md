# Vercel Deployment Guide

## Deployment Architecture

Since Vercel is a Node.js/serverless platform, we need to deploy the Python API separately.

### Recommended Setup

**Frontend (Next.js Dashboard)** → Deploy to **Vercel**
**Backend (Python API)** → Deploy to **Railway**, **Render**, or **AWS Lambda**

---

## Option 1: Vercel + Railway (Recommended)

### Step 1: Deploy Python API to Railway

1. Create account at [railway.app](https://railway.app)
2. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

3. Create `Procfile` in `/api` directory:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. Deploy:
   ```bash
   cd api
   railway login
   railway init
   railway up
   ```

5. Note your Railway API URL (e.g., `https://your-app.railway.app`)

### Step 2: Deploy Dashboard to Vercel

1. Update `.env.local`:
   ```bash
   NEXT_PUBLIC_API_URL=https://your-app.railway.app
   ```

2. Deploy to Vercel:
   ```bash
   npm install -g vercel
   vercel
   ```

3. Set environment variable in Vercel:
   - Go to Vercel dashboard → Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL` = `https://your-app.railway.app`

---

## Option 2: Vercel + Render

### Deploy Python API to Render

1. Create account at [render.com](https://render.com)
2. Create new **Web Service**
3. Connect your GitHub repo
4. Set build command: `pip install -r api/requirements.txt`
5. Set start command: `cd api && uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Deploy and note URL

### Deploy Dashboard to Vercel (same as above)

---

## Option 3: All-in-One on Vercel (Serverless Functions)

You can convert the Python API to Next.js API routes, but this requires rewriting the Python code in TypeScript/JavaScript.

**Not recommended** due to complexity of porting numerical libraries.

---

## Files for Railway Deployment

### api/Procfile
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### api/runtime.txt
```
python-3.11
```

### .gitignore
```
api/venv/
api/__pycache__/
node_modules/
.next/
.env.local
.vercel
```

---

## Environment Variables

### Development (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production (Vercel Environment Variables)
```
NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
```

---

## CORS Configuration

Update `api/config.py` to allow Vercel domain:

```python
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://your-vercel-app.vercel.app",  # Add your Vercel domain
    "https://*.vercel.app",  # Allow all Vercel preview deployments
]
```

---

## Quick Deploy Commands

```bash
# 1. Deploy API to Railway
cd api
railway login
railway init
railway up
# Note the URL: https://xxx.railway.app

# 2. Update environment variable
echo "NEXT_PUBLIC_API_URL=https://xxx.railway.app" > ../.env.local

# 3. Deploy to Vercel
cd ..
vercel --prod

# 4. Set env var in Vercel dashboard
# NEXT_PUBLIC_API_URL = https://xxx.railway.app
```

---

## Cost Estimates

- **Vercel**: Free tier (hobby projects)
- **Railway**: $5/month starter plan
- **Render**: Free tier available (with some limitations)

---

## Alternative: Docker Deployment

If you prefer Docker, you can deploy both to platforms like:
- **Fly.io**
- **DigitalOcean App Platform**
- **Google Cloud Run**

This allows keeping Python + Next.js in one container.
