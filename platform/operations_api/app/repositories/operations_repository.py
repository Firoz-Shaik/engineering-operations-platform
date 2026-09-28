from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.service import Service as ServiceModel
from app.schemas.service import ServiceCreate, ServiceUpdate

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

    async def update_service(
        self, db: AsyncSession, *, service_id: UUID, obj_in: ServiceUpdate
    ) -> ServiceModel | None:
        result = await db.execute(
            select(ServiceModel).where(ServiceModel.id == service_id)
        )
        service = result.scalar_one_or_none()
        if service is None:
            return None

        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(service, field, value)

        await db.commit()
        updated_result = await db.execute(
            select(ServiceModel)
            .options(selectinload(ServiceModel.environment))
            .where(ServiceModel.id == service_id)
        )
        return updated_result.scalar_one()

    async def delete_service(self, db: AsyncSession, *, service_id: UUID) -> bool:
        result = await db.execute(
            select(ServiceModel).where(ServiceModel.id == service_id)
        )
        service = result.scalar_one_or_none()
        if service is None:
            return False

        await db.delete(service)
        await db.commit()
        return True

    async def update_service_status(
        self, db: AsyncSession, *, service_id: UUID, service_status: str
    ) -> None:
        result = await db.execute(
            select(ServiceModel).where(ServiceModel.id == service_id)
        )
        service = result.scalar_one_or_none()
        if service is None:
            return
        service.status = service_status
        await db.commit()

operations_repository = OperationsRepository()