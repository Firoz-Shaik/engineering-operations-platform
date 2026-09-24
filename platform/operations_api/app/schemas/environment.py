from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class EnvironmentRead(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)

class EnvironmentCreate(BaseModel):
    name: str