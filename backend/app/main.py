from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path

# Setup logging to file
log_dir = Path(__file__).parent.parent.parent / "log"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "backend.log"

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize settings BEFORE importing other app modules
# This ensures LangSmith env vars are set before @traceable is evaluated
from app.config import get_settings
settings = get_settings()

# Now import other app modules (after settings are initialized)
from app.api import health, auth, chat, documents, logs


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info(f"Starting app in {settings.app_env} mode")
    if settings.langsmith_tracing:
        logger.info(f"LangSmith tracing enabled for project: {settings.langsmith_project}")
    yield
    logger.info("Shutting down app")


app = FastAPI(
    title="Agentic RAG API",
    description="Backend API for the Agentic RAG Masterclass application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(logs.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.app_env
    }
