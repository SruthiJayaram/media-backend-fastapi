from fastapi import FastAPI
from app.database import engine, Base
from app.auth import router as auth_router
from app.media import router as media_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Media Platform Backend",
    description="Upload media and generate secure streaming links",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(media_router)

@app.get("/")
def root():
    return {"message": "Media Platform Backend API"}