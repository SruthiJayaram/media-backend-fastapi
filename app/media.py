from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from pathlib import Path
from typing import Literal
from datetime import datetime, date, timedelta
from collections import defaultdict
from app.database import get_db
from app import models
from app.schemas import MediaCreateOut, StreamURLOut, ViewLogOut, AnalyticsOut
from app.security import get_current_user
from app.config import settings
from app.utils import generate_stream_url, verify_stream_signature
from app.cache import cache_service
from app.rate_limiter import rate_limit_dependency
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/media", tags=["media"])

STORAGE = Path(settings.STORAGE_DIR)
STORAGE.mkdir(exist_ok=True, parents=True)

@router.post("/", response_model=MediaCreateOut)
def create_media(
    title: str = Form(...),
    type: Literal["video", "audio"] = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    # save file to storage
    suffix = Path(file.filename or "").suffix.lower()
    safe_name = f"{uuid.uuid4().hex}{suffix}"
    dest = STORAGE / safe_name

    with dest.open("wb") as f:
        content = file.file.read()
        f.write(content)

    # create record
    media = models.MediaAsset(
        title=title,
        type=models.MediaType(type),
        file_url=str(dest.resolve())
    )
    db.add(media)
    db.commit()
    db.refresh(media)

    return MediaCreateOut(
        id=media.id,
        title=media.title,
        type=media.type.value,
        file_url=media.file_url
    )

@router.get("/{media_id}/stream-url", response_model=StreamURLOut)
def get_stream_url(
    media_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    media = db.query(models.MediaAsset).filter(models.MediaAsset.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    url = generate_stream_url(media_id)
    return StreamURLOut(stream_url=url)

# Public streaming endpoint (no auth required)
@router.get("/stream/{media_id}")
def stream_media(
    media_id: int,
    exp: int,
    sig: str,
    request: Request,
    db: Session = Depends(get_db),
):
    # verify signature
    path = f"/media/stream/{media_id}"
    if not verify_stream_signature(path, exp, sig):
        raise HTTPException(status_code=403, detail="Invalid or expired link")
    
    # find media
    media = db.query(models.MediaAsset).filter(models.MediaAsset.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # log the view
    client_ip = request.client.host if request.client else "unknown"
    log_entry = models.MediaViewLog(media_id=media_id, viewed_by_ip=client_ip)
    db.add(log_entry)
    db.commit()
    
    # serve file
    file_path = Path(media.file_url)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=file_path,
        filename=f"{media.title}{file_path.suffix}",
        media_type="application/octet-stream"
    )

# Task 2: Manual view logging endpoint with Task 3 rate limiting
@router.post("/{media_id}/view", response_model=ViewLogOut)
def log_media_view(
    media_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),  # JWT protected
    rate_limit_info = Depends(rate_limit_dependency)  # Task 3: Rate limiting
):
    """
    Manually log a media view with IP and timestamp.
    Requires JWT authentication.
    Task 3: Rate limited to prevent abuse.
    """
    # Check if media exists
    media = db.query(models.MediaAsset).filter(models.MediaAsset.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Create view log entry
    view_log = models.MediaViewLog(
        media_id=media_id,
        viewed_by_ip=client_ip
    )
    db.add(view_log)
    db.commit()
    db.refresh(view_log)
    
    # Task 3: Invalidate analytics cache when new view is added
    cache_service.invalidate_analytics(media_id)
    
    logger.info(f"📊 View logged for media {media_id} by {client_ip}")
    
    return ViewLogOut(
        message="View logged successfully",
        media_id=media_id,
        timestamp=view_log.timestamp,
        viewer_ip=client_ip
    )

# Task 2: Analytics endpoint with Task 3 caching
@router.get("/{media_id}/analytics", response_model=AnalyticsOut)
def get_media_analytics(
    media_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),  # JWT protected
):
    """
    Get analytics for a specific media asset.
    Requires JWT authentication.
    Task 3: Cached for performance optimization.
    """
    # Check if media exists
    media = db.query(models.MediaAsset).filter(models.MediaAsset.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Task 3: Try to get from cache first
    cached_analytics = cache_service.get_analytics(media_id)
    if cached_analytics:
        logger.info(f"📈 Analytics cache hit for media {media_id}")
        return cached_analytics
    
    # Calculate analytics from database
    total_views = db.query(func.count(models.MediaViewLog.id)).filter(
        models.MediaViewLog.media_id == media_id
    ).scalar() or 0
    
    unique_viewers = db.query(func.count(func.distinct(models.MediaViewLog.viewed_by_ip))).filter(
        models.MediaViewLog.media_id == media_id
    ).scalar() or 0
    
    recent_views = db.query(func.count(models.MediaViewLog.id)).filter(
        models.MediaViewLog.media_id == media_id,
        models.MediaViewLog.timestamp >= (datetime.utcnow() - timedelta(days=7))
    ).scalar() or 0
    
    analytics_data = AnalyticsOut(
        media_id=media_id,
        media_filename=media.title,
        total_views=total_views,
        unique_viewers=unique_viewers,
        recent_views_7days=recent_views,
        upload_date=media.created_at
    )
    
    # Task 3: Cache the analytics data
    cache_service.set_analytics(media_id, analytics_data)
    
    logger.info(f"📊 Analytics calculated and cached for media {media_id}")
    
    return analytics_data