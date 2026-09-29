from fastapi import APIRouter

from app.api.v1.endpoints import notifications


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["notifications"],
)