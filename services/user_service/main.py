from app.api.v1.api import api_router
from fastapi import FastAPI

app = FastAPI(
    title="User Service",
    description="User Service",
    version="1.0.0",
    docs_url="/api/v1/users/docs",
    redoc_url="/api/v1/users/redoc",
    openapi_url="/api/v1/users/openapi.json",
)


app.include_router(api_router, prefix="/api")