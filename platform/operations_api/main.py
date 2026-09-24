from app.api.v1.api import api_router
from fastapi import FastAPI

app = FastAPI(
    title="Operations API",
    description="Operations API",
    version="1.0.0",
    docs_url="/api/v1/operations/docs",
    redoc_url="/api/v1/operations/redoc",
    openapi_url="/api/v1/operations/openapi.json",
)


app.include_router(api_router, prefix="/api")