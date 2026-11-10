import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger
from app.core.middleware import AuditLoggingMiddleware
from app.api.v1.router import api_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and directories are ready
    logger.info("Initializing Code Intelligence Studio Backend...")
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    settings.ARTIFACTS_ROOT.mkdir(parents=True, exist_ok=True)
    settings.LOGS_ROOT.mkdir(parents=True, exist_ok=True)
    init_db()
    logger.info("Database schemas and runtime storage directories verified.")
    yield
    # Shutdown
    logger.info("Code Intelligence Studio Backend stopping.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="Autonomous AI Software Engineering & Repository Intelligence Platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Audit Logging Middleware
app.add_middleware(AuditLoggingMiddleware)

# API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "database": "sqlite_connected" if "sqlite" in settings.DATABASE_URL else "postgres_connected",
        "version": "0.1.0",
    }
