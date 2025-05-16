from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.api import auth, file_upload, ai_teacher
from backend.app.core import logging_config  # noqa: F401
from sqlalchemy.exc import OperationalError
from backend.app.core.database import get_db
import redis
from backend.app.core.config import get_settings
import logging
from sqlalchemy import text

app = FastAPI(
    title="AI Tutor API",
    description="Backend API for the AI Tutor platform",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(file_upload.router, prefix="/api/v1/files")
app.include_router(ai_teacher.router, prefix="/api/v1/ai")

settings = get_settings()

@app.get("/")
async def root():
    """Root endpoint returning API status."""
    return JSONResponse(
        content={
            "status": "healthy",
            "message": "AI Tutor API is running",
            "version": "0.1.0",
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    # API status
    api_status = "up"

    # Database status
    db_status = "up"
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
    except OperationalError as e:
        logging.error(f"Database OperationalError: {e}")
        db_status = "down"
    except Exception as e:
        logging.error(f"Database Exception: {e}")
        db_status = "error"

    # Redis status
    redis_status = "not_configured"
    if hasattr(settings, "REDIS_HOST") and settings.REDIS_HOST:
        try:
            r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=getattr(settings, "REDIS_PASSWORD", None))
            if r.ping():
                redis_status = "up"
            else:
                redis_status = "down"
        except Exception:
            redis_status = "error"

    # AI Models status (placeholder)
    ai_models_status = "not_configured"

    return JSONResponse(
        content={
            "status": "healthy",
            "services": {
                "api": api_status,
                "database": db_status,
                "redis": redis_status,
                "ai_models": ai_models_status,
            }
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 