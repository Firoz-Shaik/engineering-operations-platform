from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints


class DeploymentCreate(BaseModel):
    service_id: UUID
    target_version: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    idempotency_key: Annotated[str, StringConstraints(min_length=1, max_length=128)]


class DeploymentRead(BaseModel):
    id: UUID
    service_id: UUID
    target_version: str
    idempotency_key: str
    state: str
    attempts: int
    error: str | None
    execution_mode: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)