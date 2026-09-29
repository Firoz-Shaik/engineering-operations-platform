import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import text

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.tasks.celery_app import celery_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    yield
    await app.state.redis.aclose()
    await engine.dispose()


app = FastAPI(title="Notification Service", version="1.0.0", lifespan=lifespan)
app.include_router(api_router)


@app.get("/health", include_in_schema=False)
async def liveness():
    return {"service": "notification_service", "status": "alive"}


@app.get("/ready", include_in_schema=False)
async def readiness():
    components: dict[str, str] = {
        "database": "unavailable",
        "redis": "unavailable",
        "worker": "unavailable",
    }
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
        worker_responses = await asyncio.to_thread(
            celery_app.control.ping, timeout=1.0
        )
        if worker_responses:
            components["worker"] = "ready"
    except Exception:
        pass

    if not all(value == "ready" for value in components.values()):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "components": components},
        )
    return {"status": "ready", "components": components}