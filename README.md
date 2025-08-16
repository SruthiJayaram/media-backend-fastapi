# Media Platform Backend (FastAPI)

A compact, production‑style starter for a media platform where admins upload media and generate secure 10‑minute streaming links.

## Tech Choices & Assumptions

- **Language/Framework**: Python 3.11 + FastAPI (async, type hints, great DX).
- **Auth**: JWT (HS256) using python-jose with password hashing via passlib[bcrypt].
- **DB**: SQLite (via SQLAlchemy). Easy to swap to Postgres/MySQL.
- **Storage**: Local folder `./storage/` for uploaded files. In real deployments replace with S3/GCS/Azure Blob and use their native presigned URLs.
- **Secure Stream URLs**: Signed HMAC link with exp timestamp (epoch seconds), valid 10 minutes.
- **Logging**: Every stream request logs media_id, viewer IP, timestamp in MediaViewLog.
- **Scope**: Minimal, focused on the assignment requirements; no background tasks, no thumbnails, no chunked streaming.

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
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with your secrets

uvicorn app.main:app --reload --port 8000
```

Open: http://127.0.0.1:8000/docs for interactive API.
