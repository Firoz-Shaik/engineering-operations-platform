from app.api.v1.api import api_router
from fastapi import FastAPI

app = FastAPI(
    title="User Service",
    description="User Service",
    version="1.0.0",
    docs_url="/user_service/api/docs",
    redoc_url="/user_service/api/redoc",
    openapi_url="/user_service/api/openapi.json",
)


app.include_router(api_router, prefix="/api")