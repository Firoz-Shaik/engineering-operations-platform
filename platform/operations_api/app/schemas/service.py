from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.schemas.environment import EnvironmentRead


class Service(BaseModel):
    id: UUID
    name: str
    environment_id: UUID
    base_url: str
    health_enpoint: str
    version: str
    status: str
    environment: EnvironmentRead | None = None

    model_config = ConfigDict(from_attributes=True)

class ServiceCreate(BaseModel):
    name: str
    environment_id: UUID
    base_url: str
    health_enpoint: str
    version: str
    status: str

class ServiceUpdate(BaseModel):
    name: str | None = None
    base_url: str | None = None
    health_enpoint: str | None = None
    version: str | None = None
    status: str | None = None
