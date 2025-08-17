from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from typing import Literal
from app.database import get_db
from app import models
from app.schemas import MediaCreateOut, StreamURLOut
from app.security import get_current_user
from app.config import settings
from app.utils import generate_stream_url, verify_stream_signature
import uuid

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