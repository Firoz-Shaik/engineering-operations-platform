import asyncio
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, UserRoles
from app.schemas.user import UserCreate

from app.core.security import get_password_hash

class UserRepository:
    async def get_all_users(self, db: AsyncSession) -> list[User]:
        result = await db.execute(
            select(User)
            .options(selectinload(User.user_roles).selectinload(UserRoles.role))
            .where(User.deleted_at.is_(None))
        )
        return result.scalars().all()
    
    async def get_user_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        result = await db.execute(
            select(User)
            .options(selectinload(User.user_roles).selectinload(UserRoles.role))
            .where(User.email == email, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, db: AsyncSession, *, user_id: UUID) -> User | None:
        result = await db.execute(
            select(User)
            .options(selectinload(User.user_roles).selectinload(UserRoles.role))
            .where(User.id == user_id, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def create_user(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        existing_user = await self.get_user_by_email(db, email=obj_in.email)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        hashed_password = await asyncio.to_thread(get_password_hash, obj_in.password)
        db_obj = User(
            email=obj_in.email,
            hashed_password=hashed_password,
            full_name=obj_in.full_name,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_user(self, db: AsyncSession, *, user_id: UUID, obj_in: User) -> User:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            for attr, value in obj_in.dict(exclude_unset=True).items():
                setattr(user, attr, value)
            await db.commit()
            await db.refresh(user)
        return user

    async def delete_user(self, db: AsyncSession, *, user_id: str) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.deleted_at = datetime.now()
            await db.commit()
        return user

user_repository = UserRepository()


