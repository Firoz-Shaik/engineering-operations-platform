import asyncio

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.notification_repository import notification_repository
from app.schemas.notification import NotificationAccepted, OrderNotificationCreate
from app.tasks.notifications import process_notification


class NotificationService:
    async def enqueue_order_confirmation(
        self, db: AsyncSession, *, data: OrderNotificationCreate
    ) -> NotificationAccepted:
        job, created = await notification_repository.create_or_get_order_notification(
            db, data=data
        )
        if not created:
            return NotificationAccepted(id=job.id, state=job.state, duplicate=True)

        try:
            await asyncio.to_thread(
                process_notification.apply_async,
                args=[str(job.id)],
                task_id=str(job.id),
            )
        except Exception as exc:
            job.state = "failed"
            job.last_error = "Unable to enqueue notification worker job"
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Notification queue is unavailable",
            ) from exc

        return NotificationAccepted(id=job.id, state="queued", duplicate=False)


notification_service = NotificationService()