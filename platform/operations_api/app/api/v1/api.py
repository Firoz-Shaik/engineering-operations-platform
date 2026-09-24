from app.api.v1.endpoints import services, environments
from fastapi import APIRouter

api_router = APIRouter(prefix="/v1")

api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(environments.router, prefix="/environments", tags=["environments"])

@api_router.get("/health/")
async def health_check():
    return {"service": "operations_api", "status": "Healthy", "version": "1.0.0"}