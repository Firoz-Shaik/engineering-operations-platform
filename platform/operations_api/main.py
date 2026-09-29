import asyncio
from contextlib import asynccontextmanager

from app.api.v1.api import api_router
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from sqlalchemy import text

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.tasks.celery_app import celery_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    yield
    await app.state.redis.aclose()
    await engine.dispose()

app = FastAPI(
    title="Operations API",
    description="Operations API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/v1/operations/docs",
    redoc_url="/api/v1/operations/redoc",
    openapi_url="/api/v1/operations/openapi.json",
)


app.include_router(api_router, prefix="/api")


@app.get("/health", include_in_schema=False)
async def health_check():
    return {"service": "operations_api", "status": "healthy"}


@app.get("/ready", include_in_schema=False)
async def readiness_check():
    components = {"database": "unavailable", "redis": "unavailable", "worker": "unavailable"}
    try:
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
        components["database"] = "ready"
    except Exception:
        pass
    try:
        if await app.state.redis.ping():
            components["redis"] = "ready"
    except Exception:
        pass
    try:
        worker_responses = await asyncio.to_thread(celery_app.control.ping, timeout=1.0)
        if worker_responses:
            components["worker"] = "ready"
    except Exception:
        pass

    if any(value != "ready" for value in components.values()):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "components": components},
        )
    return {"status": "ready", "components": components}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)