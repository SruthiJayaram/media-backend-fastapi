from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    # JWT Configuration
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev")
    JWT_ALG: str = os.getenv("JWT_ALG", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # Stream URL Configuration
    STREAM_SIGNING_SECRET: str = os.getenv("STREAM_SIGNING_SECRET", "dev_stream")
    STREAM_LINK_TTL_SECONDS: int = int(os.getenv("STREAM_LINK_TTL_SECONDS", "600"))

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./media.db")

    # Storage Configuration
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "./storage")
    BASE_EXTERNAL_URL: str = os.getenv("BASE_EXTERNAL_URL", "http://127.0.0.1:8000")

    # Redis Configuration (Task 3)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes default

    # Rate Limiting Configuration (Task 3)
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

settings = Settings()