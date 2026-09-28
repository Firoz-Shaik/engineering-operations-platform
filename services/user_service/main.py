from app.api.v1.api import api_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="User Service",
    description="User Service",
    version="1.0.0",
    docs_url="/api/v1/users/docs",
    redoc_url="/api/v1/users/redoc",
    openapi_url="/api/v1/users/openapi.json",
)


app.include_router(api_router, prefix="/api")


@app.get("/health", include_in_schema=False)
async def health_check():
    return {"service": "user_service", "status": "healthy"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)