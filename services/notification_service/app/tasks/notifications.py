import asyncio
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.models.notification import NotificationJob
from app.tasks.celery_app import celery_app


logger = logging.getLogger(__name__)


async def _process_notification(job_id: UUID, attempt: int) -> None:
    worker_engine = create_async_engine(
        settings.DATABASE_URL, poolclass=NullPool, pool_pre_ping=True
    )
    session_factory = async_sessionmaker(worker_engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            result = await session.execute(
                select(NotificationJob).where(NotificationJob.id == job_id)
            )
            job = result.scalar_one_or_none()
            if job is None or job.state == "success":
                return

            job.state = "running"
            job.attempts = attempt
            job.last_error = None
            await session.commit()

            # Local adapter: replace with an email/SMS provider integration.
            logger.info(
                "notification processed id=%s type=%s",
                job.id,
                job.event_type,
            )
            job.state = "success"
            await session.commit()
    except Exception as exc:
        async with session_factory() as session:
            result = await session.execute(
                select(NotificationJob).where(NotificationJob.id == job_id)
            )
            job = result.scalar_one_or_none()
            if job is not None:
                job.state = "retrying" if attempt <= settings.NOTIFICATION_MAX_RETRIES else "failed"
                job.attempts = attempt
                job.last_error = str(exc)[:1000]
                await session.commit()
        raise
    finally:
        await worker_engine.dispose()


@celery_app.task(
    bind=True,
    name="notification_service.process_notification",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    max_retries=settings.NOTIFICATION_MAX_RETRIES,
)
def process_notification(self, job_id: str) -> None:
    asyncio.run(_process_notification(UUID(job_id), self.request.retries + 1))