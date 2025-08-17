# FastAPI Media Backend - Complete Testing & Usage Guide

## 🚀 How to Run

### Start the Server
```bash
cd /workspaces/media-backend-fastapi
./run.sh
# OR
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Access the API
- **Swagger UI**: https://glorious-space-fortnight-r44www696r4hwjjx-8000.app.github.dev/docs
- **ReDoc**: https://glorious-space-fortnight-r44www696r4hwjjx-8000.app.github.dev/redoc
- **Root**: https://glorious-space-fortnight-r44www696r4hwjjx-8000.app.github.dev/

## 🧪 Testing the API

### 1. Test Root Endpoint
```bash
curl http://127.0.0.1:8000/
```
Expected: `{"message": "Media Platform Backend API"}`

### 2. Create User Account
```bash
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password123"}'
```
Expected: `{"access_token": "...", "token_type": "bearer"}`

### 3. Login (Alternative to Signup)
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password123"}'
```

### 4. Upload Media (Replace YOUR_TOKEN)
```bash
# Create a test file first
echo "Test video content" > test_video.mp4

# Upload with authentication
curl -X POST http://127.0.0.1:8000/media/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=My Test Video" \
  -F "type=video" \
  -F "file=@test_video.mp4"
```
Expected: `{"id": 1, "title": "My Test Video", "type": "video", "file_url": "..."}`

### 5. Get Stream URL (Replace YOUR_TOKEN and MEDIA_ID)
```bash
curl -X GET http://127.0.0.1:8000/media/1/stream-url \
  -H "Authorization: Bearer YOUR_TOKEN"
```
Expected: `{"stream_url": "https://...?exp=...&sig=..."}`

### 6. Test Streaming (No auth needed - uses signed URL)
```bash
curl -I "THE_STREAM_URL_FROM_STEP_5"
```
Expected: HTTP 200 with file headers

### 7. Log Media View (Task 2 - NEW)
```bash
curl -X POST http://127.0.0.1:8000/media/1/view \
  -H "Authorization: Bearer YOUR_TOKEN"
```
Expected: `{"message": "View logged successfully", "media_id": 1, "timestamp": "...", "viewer_ip": "..."}`

### 8. Get Analytics (Task 2 - NEW)
```bash
curl -X GET http://127.0.0.1:8000/media/1/analytics \
  -H "Authorization: Bearer YOUR_TOKEN"
```
Expected:
```json
{
  "total_views": 3,
  "unique_ips": 1,
  "views_per_day": {
    "2025-08-17": 3
  }
}
```

## 📊 Database & Files

### Check Database
```bash
# View SQLite database (if sqlite3 is installed)
sqlite3 media.db ".tables"
sqlite3 media.db "SELECT * FROM admin_users;"
sqlite3 media.db "SELECT * FROM media_assets;"
sqlite3 media.db "SELECT * FROM media_view_logs;"
```

### Check Uploaded Files
```bash
ls -la storage/
```

## 🔧 Configuration

### Environment Variables (.env)
```env
JWT_SECRET=your-secret-key
STREAM_SIGNING_SECRET=your-stream-secret
DATABASE_URL=sqlite:///./media.db
STORAGE_DIR=./storage
BASE_EXTERNAL_URL=https://your-domain.com
```

## 🛠️ Development Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
python test_api.py  # Automated tests
./test_manual.sh    # Manual test script
```

### Check Server Logs
The server logs show in the terminal where you started uvicorn.

## 🌐 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | No | API status |
| POST | `/auth/signup` | No | Create account |
| POST | `/auth/login` | No | Login |
| POST | `/media/` | Yes | Upload media |
| GET | `/media/{id}/stream-url` | Yes | Get signed URL |
| GET | `/media/stream/{id}` | Signed | Stream file |
| **POST** | **`/media/{id}/view`** | **Yes** | **Log media view (Task 2)** |
| **GET** | **`/media/{id}/analytics`** | **Yes** | **Get view analytics (Task 2)** |

## 🔐 Security Features

- **JWT Authentication**: Bearer tokens for API access
- **Password Hashing**: bcrypt for secure password storage
- **Signed URLs**: HMAC-signed streaming links with 10-min expiration
- **Input Validation**: Pydantic schemas for request validation
- **View Logging**: Track all media access with IP and timestamp

## 🚨 Troubleshooting

### Server Won't Start
- Check if port 8000 is already in use: `lsof -i :8000`
- Check Python dependencies: `pip install -r requirements.txt`

### Authentication Errors
- Verify JWT_SECRET is set in .env
- Check token format: `Authorization: Bearer your_token_here`

### File Upload Issues
- Ensure storage/ directory exists and is writable
- Check file size limits (FastAPI default is 16MB)

### Stream URL Errors
- Verify STREAM_SIGNING_SECRET in .env
- Check if URL has expired (10-minute limit)
- Ensure BASE_EXTERNAL_URL matches your domain

## 📈 Production Deployment

### For Production
1. Use PostgreSQL instead of SQLite
2. Set up cloud storage (S3, GCS, Azure Blob)
3. Use environment-specific secrets
4. Add rate limiting
5. Set up HTTPS
6. Use a production WSGI server (gunicorn)

### Example Production Command
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
