from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev")
    JWT_ALG: str = os.getenv("JWT_ALG", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    STREAM_SIGNING_SECRET: str = os.getenv("STREAM_SIGNING_SECRET", "dev_stream")
    STREAM_LINK_TTL_SECONDS: int = int(os.getenv("STREAM_LINK_TTL_SECONDS", "600"))

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./media.db")

    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "./storage")
    BASE_EXTERNAL_URL: str = os.getenv("BASE_EXTERNAL_URL", "http://127.0.0.1:8000")

settings = Settings()