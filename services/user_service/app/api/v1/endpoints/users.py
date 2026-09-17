from uuid import UUID

from fastapi import APIRouter, status, HTTPException
from app.services.user_service import user_service
from app.schemas.user import RoleAssignmentRequest, RoleRead, User, UserCreate, UserUpdate
from app.api.deps import AdminUser, DBSession, CurrentUser
from pydantic import EmailStr
from app.services.role_service import role_service


router = APIRouter()

users = {}
@router.get("/", response_model=list[User], status_code=status.HTTP_200_OK)
async def get_users(
    db: DBSession,
    current_user: AdminUser,
):
    return await user_service.get_all_users(db)

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(db: DBSession, user: UserCreate, current_user: AdminUser):
    return await user_service.create_user(db, obj_in=user)


@router.post("/{user_id}/roles", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def assign_role_to_user(
    db: DBSession,
    user_id: UUID,
    payload: RoleAssignmentRequest,
    current_user: AdminUser,
):
    user = await user_service.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return await role_service.assign_role_to_user(
        db, user=user, role_name=payload.role_name
    )

@router.get("/me", response_model=User, status_code=status.HTTP_200_OK)
async def get_current_user_details(current_user: CurrentUser):
    return current_user

@router.get("/by-email/{email}", response_model=User, status_code=status.HTTP_200_OK)
async def get_user_by_email(
    db: DBSession,
    email: EmailStr,
    current_user: AdminUser,
):
    user = await user_service.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.get("/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def get_user_by_id(
    db: DBSession,
    user_id: UUID,
    current_user: AdminUser,
):
    user = await user_service.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(
    db: DBSession,
    user_id: UUID,
    user: UserUpdate,
    current_user: CurrentUser,
):
    user = await user_service.update_user(db, user_id=user_id, obj_in=user)

    return user