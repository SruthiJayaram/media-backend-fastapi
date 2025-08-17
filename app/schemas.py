from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Dict
from datetime import datetime

class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MediaCreateOut(BaseModel):
    id: int
    title: str
    type: Literal["video", "audio"]
    file_url: str

class StreamURLOut(BaseModel):
    stream_url: str

class ViewLogOut(BaseModel):
    message: str
    media_id: int
    timestamp: datetime
    viewer_ip: str

class AnalyticsOut(BaseModel):
    total_views: int
    unique_ips: int
    views_per_day: Dict[str, int]