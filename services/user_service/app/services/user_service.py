# app/services/user_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.user import User
from app.schemas.user import UserCreate
from app.repositories.user_repository import user_repository
from app.services.role_service import role_service

class UserService:
    async def get_all_users(self, db: AsyncSession) -> list[User]:
        return await user_repository.get_all_users(db)

    async def get_user_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        user = await user_repository.get_user_by_email(db, email=email)
        return user

    async def get_user_by_id(self, db: AsyncSession, *, user_id: UUID) -> User | None:
        user = await user_repository.get_user_by_id(db, user_id=user_id)
        return user

    async def create_user(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        role_names = await role_service.validate_role_names(db, role_names=obj_in.roles)
        user = await user_repository.create_user(db, obj_in=obj_in)
        for role_name in role_names:
            await role_service.assign_role_to_user(db, user=user, role_name=role_name)
        return await user_repository.get_user_by_id(db, user_id=user.id)

    async def update_user(self, db: AsyncSession, *, user_id: UUID, obj_in: User) -> User:
        user = await user_repository.update_user(db, user_id=user_id, obj_in=obj_in)
        return user

    async def delete_user(self, db: AsyncSession, *, user_id: str) -> User | None:
        user = await user_repository.delete_user(db, user_id=user_id)
        return user

user_service = UserService()


