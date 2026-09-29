import asyncio
from uuid import UUID

from celery.exceptions import MaxRetriesExceededError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.models.deployment import Deployment
from app.models.service import Service
from app.tasks.celery_app import celery_app


async def _execute_deployment(deployment_id: UUID, attempt: int) -> None:
    worker_engine = create_async_engine(
        settings.DATABASE_URL, poolclass=NullPool, pool_pre_ping=True
    )
    session_factory = async_sessionmaker(worker_engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            result = await session.execute(
                select(Deployment).where(Deployment.id == deployment_id)
            )
            deployment = result.scalar_one_or_none()
            if deployment is None or deployment.state == "SUCCESS":
                return

            deployment.state = "RUNNING"
            deployment.attempts = attempt
            deployment.error = None
            await session.commit()

            service_result = await session.execute(
                select(Service).where(Service.id == deployment.service_id)
            )
            service = service_result.scalar_one_or_none()
            if service is None:
                deployment.state = "FAILED"
                deployment.error = "Registered service no longer exists"
            else:
                # Day 7 local executor updates registry metadata only; AWS rollout
                # requires a provider-specific deployment adapter.
                service.version = deployment.target_version
                deployment.state = "SUCCESS"
            await session.commit()
    finally:
        await worker_engine.dispose()


@celery_app.task(
    bind=True,
    name="operations_api.execute_deployment",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=120,
    retry_jitter=True,
    max_retries=settings.DEPLOYMENT_MAX_RETRIES,
)
def execute_deployment(self, deployment_id: str) -> None:
    try:
        asyncio.run(_execute_deployment(UUID(deployment_id), self.request.retries + 1))
    except Exception:
        if self.request.retries >= settings.DEPLOYMENT_MAX_RETRIES:
            asyncio.run(_mark_failed(UUID(deployment_id), "Deployment worker exhausted retries"))
        raise


async def _mark_failed(deployment_id: UUID, message: str) -> None:
    worker_engine = create_async_engine(
        settings.DATABASE_URL, poolclass=NullPool, pool_pre_ping=True
    )
    session_factory = async_sessionmaker(worker_engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            result = await session.execute(
                select(Deployment).where(Deployment.id == deployment_id)
            )
            deployment = result.scalar_one_or_none()
            if deployment is not None:
                deployment.state = "FAILED"
                deployment.error = message
                await session.commit()
    finally:
        await worker_engine.dispose()