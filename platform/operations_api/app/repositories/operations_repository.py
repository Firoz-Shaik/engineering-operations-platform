from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.service import Service as ServiceModel
from app.schemas.service import ServiceCreate

class OperationsRepository:
    async def get_all_services(self, db: AsyncSession) -> list[ServiceModel]:
        stmt = select(ServiceModel).options(selectinload(ServiceModel.environment))
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_service_by_id(self, db: AsyncSession, *, service_id: UUID) -> ServiceModel | None:
        result = await db.execute(
            select(ServiceModel).where(ServiceModel.id == service_id).options(selectinload(ServiceModel.environment))
        )
        return result.scalar_one_or_none()
    
    async def create_service(self, db: AsyncSession, *, obj_in: ServiceCreate) -> ServiceModel:
        service = ServiceModel(**obj_in.model_dump())
        db.add(service)
        await db.commit()
        result = await db.execute(
            select(ServiceModel)
            .options(selectinload(ServiceModel.environment))
            .where(ServiceModel.id == service.id)
        )
        return result.scalar_one()

operations_repository = OperationsRepository()