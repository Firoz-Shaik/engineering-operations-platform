from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator
from datetime import datetime
from typing import Annotated
import uuid

class Order(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    payment_id: uuid.UUID
    total_amount: float
    status: Annotated[str, StringConstraints(min_length=1)]
    created_at: datetime
    updated_at: datetime

class OrderCreate(BaseModel):
    user_id: uuid.UUID
    payment_id: uuid.UUID
    total_amount: float
    status: Annotated[str, StringConstraints(min_length=1)]

class OrderUpdate(BaseModel):
    user_id: uuid.UUID | None
    payment_id: uuid.UUID | None
    total_amount: float | None
    status: str | None