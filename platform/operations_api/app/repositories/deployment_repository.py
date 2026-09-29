from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deployment import Deployment
from app.schemas.deployment import DeploymentCreate


class DeploymentRepository:
    async def create_or_get(
        self, db: AsyncSession, *, data: DeploymentCreate
    ) -> tuple[Deployment, bool]:
        result = await db.execute(
            select(Deployment).where(
                Deployment.idempotency_key == data.idempotency_key
            )
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            if existing.state == "FAILED":
                existing.state = "QUEUED"
                existing.error = None
                await db.commit()
                await db.refresh(existing)
                return existing, True
            return existing, False

        deployment = Deployment(
            service_id=data.service_id,
            target_version=data.target_version,
            idempotency_key=data.idempotency_key,
            state="QUEUED",
        )
        db.add(deployment)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            result = await db.execute(
                select(Deployment).where(
                    Deployment.idempotency_key == data.idempotency_key
                )
            )
            return result.scalar_one(), False
        await db.refresh(deployment)
        return deployment, True

    async def get_by_id(self, db: AsyncSession, *, deployment_id: UUID) -> Deployment | None:
        result = await db.execute(
            select(Deployment).where(Deployment.id == deployment_id)
        )
        return result.scalar_one_or_none()

    async def mark_failed(self, db: AsyncSession, *, deployment_id: UUID, error: str) -> None:
        deployment = await self.get_by_id(db, deployment_id=deployment_id)
        if deployment is not None:
            deployment.state = "FAILED"
            deployment.error = error
            await db.commit()


deployment_repository = DeploymentRepository()