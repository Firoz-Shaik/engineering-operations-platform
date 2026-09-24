from uuid import UUID

from app.models.service import Environment
from app.schemas.environment import EnvironmentCreate, EnvironmentRead
from app.repositories.environments_repository import environments_repository
from sqlalchemy.ext.asyncio import AsyncSession

class EnvironmentsService:
    async def get_all_environments(self, db: AsyncSession) -> list[EnvironmentRead]:
        result = await environments_repository.get_all_environments(db=db)
        if not result:
            return []
        return result

    async def get_environment_by_id(self, db: AsyncSession, *, environment_id: UUID) -> Environment | None:
        result = await environments_repository.get_environment_by_id(db=db, environment_id=environment_id)
        if not result:
            return None
        return result

    async def create_environment(self, db: AsyncSession, *, obj_in: EnvironmentCreate) -> EnvironmentRead:
        return await environments_repository.create_environment(db=db, obj_in=obj_in)


environments_service = EnvironmentsService()