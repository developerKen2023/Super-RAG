from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.api import health, auth, chat

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    print(f"Starting app in {settings.app_env} mode")
    if settings.langsmith_tracing:
        print(f"LangSmith tracing enabled for project: {settings.langsmith_project}")
    yield
    print("Shutting down app")


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


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.app_env
    }
