from uuid import UUID
from app.models.service import Service
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.operations_repository import operations_repository
from app.schemas.service import ServiceCreate

class OperationsService:

    async def get_all_services(self, db: AsyncSession) -> list[Service]:
        result = await operations_repository.get_all_services(db)
        if not result:
            return []
        return result

    async def get_service_by_id(self, db: AsyncSession, *, service_id: UUID) -> Service | None:
        return await operations_repository.get_service_by_id(db, service_id=service_id)
    async def create_service(self, db: AsyncSession, *, obj_in: ServiceCreate) -> Service:
        return await operations_repository.create_service(db, obj_in=obj_in)

operations_service = OperationsService()