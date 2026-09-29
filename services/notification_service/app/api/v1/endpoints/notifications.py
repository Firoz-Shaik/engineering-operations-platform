from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import DBSession, InternalService
from app.repositories.notification_repository import notification_repository
from app.schemas.notification import (
    NotificationAccepted,
    NotificationRead,
    OrderNotificationCreate,
)
from app.services.notification_service import notification_service


router = APIRouter()


@router.post(
    "/order-confirmation",
    response_model=NotificationAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
async def enqueue_order_confirmation(
    data: OrderNotificationCreate,
    db: DBSession,
    _internal_service: InternalService,
):
    return await notification_service.enqueue_order_confirmation(db, data=data)


@router.get("/{job_id}", response_model=NotificationRead)
async def get_notification_job(
    job_id: UUID,
    db: DBSession,
    _internal_service: InternalService,
):
    job = await notification_repository.get_by_id(db, job_id=job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification job not found",
        )
    return job