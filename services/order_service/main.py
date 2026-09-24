from app.api.v1.api import api_router
from fastapi import FastAPI

app = FastAPI(
    title="Order Service",
    description="Order Service",
    version="1.0.0",
    docs_url="/api/v1/orders/docs",
    redoc_url="/api/v1/orders/redoc",
    openapi_url="/api/v1/orders/openapi.json",
)


app.include_router(api_router, prefix="/api")