from fastapi import APIRouter, status

from app.api.deps import AdminUser, DBSession
from app.schemas.user import RoleCreate, RoleRead
from app.services.role_service import role_service


router = APIRouter()


@router.get("/", response_model=list[RoleRead], status_code=status.HTTP_200_OK)
async def get_roles(db: DBSession, current_user: AdminUser):
    return await role_service.get_all_roles(db)


@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(db: DBSession, role: RoleCreate, current_user: AdminUser):
    return await role_service.create_role(db, obj_in=role)