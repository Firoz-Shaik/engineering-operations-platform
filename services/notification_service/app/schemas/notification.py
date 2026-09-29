from datetime import datetime
from typing import Any, Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints


class OrderNotificationCreate(BaseModel):
    idempotency_key: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    recipient: EmailStr
    order_id: UUID
    payload: dict[str, Any] = Field(default_factory=dict)


class NotificationAccepted(BaseModel):
    id: UUID
    state: str
    duplicate: bool = False


class NotificationRead(BaseModel):
    id: UUID
    idempotency_key: str
    event_type: str
    recipient: EmailStr
    payload: dict[str, Any]
    state: str
    attempts: int
    last_error: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)