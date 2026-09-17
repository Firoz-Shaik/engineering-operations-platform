from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Role, User, UserRoles
from app.schemas.user import RoleCreate


class RoleRepository:
    async def get_all(self, db: AsyncSession) -> list[Role]:
        result = await db.execute(select(Role).order_by(Role.name))
        return list(result.scalars().all())

    async def get_by_name(self, db: AsyncSession, *, name: str) -> Role | None:
        result = await db.execute(select(Role).where(Role.name == name.strip().lower()))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: RoleCreate) -> Role:
        normalized_name = obj_in.name.strip().lower()
        if await self.get_by_name(db, name=normalized_name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Role '{normalized_name}' already exists",
            )

        role = Role(name=normalized_name)
        db.add(role)
        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Role '{normalized_name}' already exists",
            ) from exc
        await db.refresh(role)
        return role

    async def has_assignment(
        self, db: AsyncSession, *, user_id: UUID, role_id: UUID
    ) -> bool:
        result = await db.execute(
            select(UserRoles.id).where(
                UserRoles.user_id == user_id,
                UserRoles.role_id == role_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def assign_to_user(
        self, db: AsyncSession, *, user: User, role_name: str
    ) -> Role:
        normalized_name = role_name.strip().lower()
        role = await self.get_by_name(db, name=normalized_name)
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{normalized_name}' does not exist",
            )
        if await self.has_assignment(db, user_id=user.id, role_id=role.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Role '{normalized_name}' is already assigned to this user",
            )

        assignment = UserRoles(user_id=user.id, role_id=role.id)
        db.add(assignment)
        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Role '{normalized_name}' is already assigned to this user",
            ) from exc
        await db.refresh(assignment, ["role"])
        return assignment.role


role_repository = RoleRepository()