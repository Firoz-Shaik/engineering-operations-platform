from uuid import UUID

from datetime import datetime
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, field_validator
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

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, value: str) -> str:
        value = value.strip().rstrip("/")
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("base_url must be an absolute http or https URL")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("base_url cannot contain credentials, query, or fragment")
        return value

class ServiceUpdate(BaseModel):
    name: str | None = None
    base_url: str | None = None
    health_enpoint: str | None = None
    version: str | None = None
    status: str | None = None

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip().rstrip("/")
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("base_url must be an absolute http or https URL")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("base_url cannot contain credentials, query, or fragment")
        return value


class ServiceHealth(BaseModel):
    service_id: UUID
    name: str
    url: str
    is_healthy: bool
    http_status: int | None = None
    response_time_ms: float
    checked_at: datetime
    error: str | None = None
