from app.api.v1.endpoints import auth, roles, users
from fastapi import APIRouter


api_router = APIRouter(prefix="/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])

@api_router.get("/health/")
async def health_check():
    return {"service": "user_service", "status": "Healthy", "version": "1.0.0"}