from uuid import UUID

from app.models.service import Environment as EnvironmentModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.environment import EnvironmentCreate, EnvironmentRead
from sqlalchemy import select
from sqlalchemy.orm import selectinload



class EnvironmentsRepository:

    async def get_all_environments(self, db: AsyncSession) -> list[EnvironmentModel]:
        result = await db.execute(select(EnvironmentModel).order_by(EnvironmentModel.name))
        return result.scalars().all()

    async def get_environment_by_id(self, db: AsyncSession, *, environment_id: UUID) -> EnvironmentModel | None:
        result = await db.execute(select(EnvironmentModel).where(EnvironmentModel.id == environment_id))
        return result.scalar_one_or_none()
    
    async def create_environment(self, db: AsyncSession, *, obj_in: EnvironmentCreate) -> EnvironmentRead:
        environment = EnvironmentModel(**obj_in.model_dump())
        db.add(environment)
        await db.commit()
        result = await db.execute(select(EnvironmentModel).where(EnvironmentModel.id == environment.id))
        return result.scalar_one()


environments_repository = EnvironmentsRepository()