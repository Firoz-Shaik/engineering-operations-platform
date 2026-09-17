from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator
from datetime import datetime
from typing import Annotated
import uuid


class UserBase(BaseModel):
    email: EmailStr
    full_name: Annotated[str, StringConstraints(min_length=1)]


class UserCreate(UserBase):
    password: Annotated[str, StringConstraints(min_length=8)]
    roles: list[str] = Field(default_factory=list)
    user_role: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes when encoded as UTF-8")
        return value

    @field_validator("roles")
    @classmethod
    def normalize_role_names(cls, value):
        if value is None:
            return []
        return [str(item).lower().strip() for item in value if str(item).strip()]

    @field_validator("user_role")
    @classmethod
    def normalize_user_role(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().lower()


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None


class RoleCreate(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1)]

    @field_validator("name")
    @classmethod
    def normalize_role_name(cls, value: str) -> str:
        return value.strip().lower()


class RoleRead(BaseModel):
    id: uuid.UUID
    name: str

    model_config = {"from_attributes": True}


class RoleAssignmentRequest(BaseModel):
    role_name: Annotated[str, StringConstraints(min_length=1)]

    @field_validator("role_name")
    @classmethod
    def normalize_role_name(cls, value: str) -> str:
        return value.strip().lower()


class User(BaseModel):
    email: EmailStr
    full_name: Annotated[str, StringConstraints(min_length=1)]
    id: uuid.UUID
    roles: list[str] = Field(default_factory=list)
    created_at: datetime
    model_config = {"from_attributes": True}