from pydantic import BaseModel, EmailStr, Field
from typing import Literal

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