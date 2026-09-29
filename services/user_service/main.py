from contextlib import asynccontextmanager

from app.api.v1.api import api_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from sqlalchemy import text

from app.core.database import SessionLocal, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(
    title="User Service",
    description="User Service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/v1/users/docs",
    redoc_url="/api/v1/users/redoc",
    openapi_url="/api/v1/users/openapi.json",
)


app.include_router(api_router, prefix="/api")


@app.get("/health", include_in_schema=False)
async def health_check():
    return {"service": "user_service", "status": "healthy"}


@app.get("/ready", include_in_schema=False)
async def readiness_check():
    try:
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not ready",
        ) from exc
    return {"status": "ready", "components": {"database": "ready"}}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)