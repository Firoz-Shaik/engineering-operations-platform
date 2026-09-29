import asyncio
import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.deployment_repository import deployment_repository
from app.repositories.operations_repository import operations_repository
from app.schemas.deployment import DeploymentCreate, DeploymentRead
from app.tasks.deployments import execute_deployment


logger = logging.getLogger(__name__)


class DeploymentService:
    async def create_deployment(
        self, db: AsyncSession, *, data: DeploymentCreate
    ) -> DeploymentRead:
        service = await operations_repository.get_service_by_id(
            db, service_id=data.service_id
        )
        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found",
            )

        deployment, created = await deployment_repository.create_or_get(db, data=data)
        if created:
            try:
                await asyncio.to_thread(
                    execute_deployment.apply_async,
                    args=[str(deployment.id)],
                    task_id=str(deployment.id),
                )
            except Exception as exc:
                await deployment_repository.mark_failed(
                    db,
                    deployment_id=deployment.id,
                    error="Deployment queue is unavailable",
                )
                logger.exception("could not enqueue deployment %s", deployment.id)
                deployment.state = "FAILED"
                deployment.error = "Deployment queue is unavailable"
                if isinstance(exc, TimeoutError):
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Deployment queue is unavailable",
                    ) from exc
        return DeploymentRead.model_validate(deployment)

    async def get_deployment(
        self, db: AsyncSession, *, deployment_id: UUID
    ) -> DeploymentRead | None:
        deployment = await deployment_repository.get_by_id(
            db, deployment_id=deployment_id
        )
        return DeploymentRead.model_validate(deployment) if deployment else None


deployment_service = DeploymentService()