from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: UUID
    email: EmailStr
    roles: list[str] = Field(default_factory=list)