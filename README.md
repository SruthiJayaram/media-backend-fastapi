# Media Platform Backend (FastAPI)

A compact, production‑style starter for a media platform where admins upload media and generate secure 10‑minute streaming links with comprehensive view tracking and analytics.

## ✅ Task Completion Status

- **✅ Task 1**: Basic media backend with authentication and secure streaming
- **✅ Task 2**: Media view tracking & analytics with JWT protection

## Tech Choices & Assumptions

- **Language/Framework**: Python 3.11 + FastAPI (async, type hints, great DX).
- **Auth**: JWT (HS256) using python-jose with password hashing via passlib[bcrypt].
- **DB**: SQLite (via SQLAlchemy). Easy to swap to Postgres/MySQL.
- **Storage**: Local folder `./storage/` for uploaded files. In real deployments replace with S3/GCS/Azure Blob and use their native presigned URLs.
- **Secure Stream URLs**: Signed HMAC link with exp timestamp (epoch seconds), valid 10 minutes.
- **Analytics**: Complete view tracking with IP logging, daily aggregations, and unique visitor counting.
- **Logging**: Every stream request logs media_id, viewer IP, timestamp in MediaViewLog.
- **Scope**: Comprehensive media platform with authentication, upload, streaming, and analytics.

## Project Structure

```
media-backend/
├─ .env.example
├─ README.md
├─ app/
│  ├─ main.py
│  ├─ config.py
│  ├─ database.py
│  ├─ models.py
│  ├─ schemas.py
│  ├─ security.py
│  ├─ auth.py
│  ├─ media.py
│  └─ utils.py
├─ storage/            # created at runtime for file uploads
├─ requirements.txt
└─ run.sh
```

## Quickstart

```bash
# Clone the repository
git clone https://github.com/SruthiJayaram/media-backend-fastapi.git
cd media-backend-fastapi

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env file with your secrets (JWT_SECRET and STREAM_SIGNING_SECRET)

# Run the server
uvicorn app.main:app --reload --port 8000
# OR use the run script: ./run.sh
```

## Access the API

Once running locally:
- **API Root**: http://127.0.0.1:8000
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Quick Test

```bash
# Test the API is working
curl http://127.0.0.1:8000/

# Create a user account
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Run automated tests
python test_complete.py
```

## Deployment Options

### Local Development
Follow the Quickstart guide above for local development.

### Docker Deployment
```bash
# Create Dockerfile (example)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Build and run
docker build -t media-backend .
docker run -p 8000:8000 media-backend
```

### Cloud Deployment
- **Heroku**: Use `Procfile` with `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Railway**: Connect GitHub repo, auto-deploys
- **DigitalOcean App Platform**: Connect repo, set build command
- **AWS/GCP**: Use container services or serverless functions

## Environment Configuration

For production deployment, update these environment variables:
```env
JWT_SECRET=your-secure-secret-key-here
STREAM_SIGNING_SECRET=your-stream-secret-here
DATABASE_URL=postgresql://user:pass@host:port/db  # For production
BASE_EXTERNAL_URL=https://your-domain.com  # Your actual domain
```
