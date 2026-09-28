from fastapi import APIRouter, status, HTTPException
from app.core.database import DBSession
from app.services.environments_service import environments_service
from app.schemas.environment import EnvironmentCreate, EnvironmentRead
from app.api.deps import AdminUser

router = APIRouter()

@router.get("/", response_model=list[EnvironmentRead], status_code=status.HTTP_200_OK)
async def get_environments(db: DBSession, current_user: AdminUser):
    return await environments_service.get_all_environments(db)

@router.post("/", response_model=EnvironmentRead, status_code=status.HTTP_201_CREATED)
async def create_environment(
    db: DBSession,
    environment: EnvironmentCreate,
    current_user: AdminUser,
):
    return await environments_service.create_environment(db, obj_in=environment)