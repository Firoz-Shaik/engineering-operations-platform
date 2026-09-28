from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from datetime import datetime
from typing import Annotated
import uuid

class Order(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    payment_id: uuid.UUID | None
    total_amount: float
    status: Annotated[str, StringConstraints(min_length=1)]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    user_id: uuid.UUID
    payment_id: uuid.UUID | None = None
    total_amount: float
    status: Annotated[str, StringConstraints(min_length=1)] = "pending"

class OrderUpdate(BaseModel):
    payment_id: uuid.UUID | None = None
    total_amount: float | None = None
    status: str | None = None