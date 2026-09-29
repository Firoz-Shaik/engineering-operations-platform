from contextlib import asynccontextmanager

from app.api.v1.api import api_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import httpx
from sqlalchemy import text

from app.core.database import SessionLocal, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(
    title="Order Service",
    description="Order Service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/v1/orders/docs",
    redoc_url="/api/v1/orders/redoc",
    openapi_url="/api/v1/orders/openapi.json",
)


app.include_router(api_router, prefix="/api")


@app.get("/health", include_in_schema=False)
async def health_check():
    return {"service": "order_service", "status": "healthy"}


@app.get("/ready", include_in_schema=False)
async def readiness_check():
    components = {"database": "unavailable", "user_service": "unavailable"}
    try:
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
        components["database"] = "ready"
    except Exception:
        pass

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{settings.USER_SERVICE_URL.rstrip('/')}/health")
        if response.is_success:
            components["user_service"] = "ready"
    except httpx.RequestError:
        pass

    if any(value != "ready" for value in components.values()):
        from fastapi import HTTPException, status

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