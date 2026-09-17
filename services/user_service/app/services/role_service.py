from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Role, User
from app.repositories.role_repository import role_repository
from app.schemas.user import RoleCreate


class RoleService:
    async def get_all_roles(self, db: AsyncSession) -> list[Role]:
        return await role_repository.get_all(db)

    async def create_role(self, db: AsyncSession, *, obj_in: RoleCreate) -> Role:
        return await role_repository.create(db, obj_in=obj_in)

    async def validate_role_names(
        self, db: AsyncSession, *, role_names: list[str]
    ) -> list[str]:
        normalized_names = [name.strip().lower() for name in role_names if name.strip()]
        if len(normalized_names) != len(set(normalized_names)):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A role cannot be assigned more than once",
            )
        for role_name in normalized_names:
            if await role_repository.get_by_name(db, name=role_name) is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Role '{role_name}' does not exist",
                )
        return normalized_names

    async def assign_role_to_user(
        self, db: AsyncSession, *, user: User, role_name: str
    ) -> Role:
        return await role_repository.assign_to_user(
            db, user=user, role_name=role_name
        )


role_service = RoleService()