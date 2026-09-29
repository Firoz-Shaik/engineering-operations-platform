from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import NotificationJob
from app.schemas.notification import OrderNotificationCreate


class NotificationRepository:
    async def get_by_id(self, db: AsyncSession, *, job_id: UUID) -> NotificationJob | None:
        result = await db.execute(
            select(NotificationJob).where(NotificationJob.id == job_id)
        )
        return result.scalar_one_or_none()

    async def create_or_get_order_notification(
        self, db: AsyncSession, *, data: OrderNotificationCreate
    ) -> tuple[NotificationJob, bool]:
        result = await db.execute(
            select(NotificationJob).where(
                NotificationJob.idempotency_key == data.idempotency_key
            )
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            if existing.state == "failed":
                existing.state = "queued"
                existing.last_error = None
                await db.commit()
                await db.refresh(existing)
                return existing, True
            return existing, False

        job = NotificationJob(
            idempotency_key=data.idempotency_key,
            event_type="order_confirmation",
            recipient=str(data.recipient),
            payload={"order_id": str(data.order_id), **data.payload},
            state="queued",
        )
        db.add(job)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            result = await db.execute(
                select(NotificationJob).where(
                    NotificationJob.idempotency_key == data.idempotency_key
                )
            )
            return result.scalar_one(), False
        await db.refresh(job)
        return job, True


notification_repository = NotificationRepository()