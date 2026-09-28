from uuid import UUID

import httpx
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.core.config import settings


class UserServiceUser(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    roles: list[str] = Field(default_factory=list)


class UserServiceClient:
    async def get_user(self, user_id: UUID) -> UserServiceUser | None:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{settings.USER_SERVICE_URL.rstrip('/')}/api/v1/users/internal/{user_id}",
                    headers={"X-Internal-API-Key": settings.INTERNAL_API_KEY},
                )
        except httpx.TimeoutException as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="User Service timed out",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="User Service is unavailable",
            ) from exc

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return None
        if response.status_code >= 500:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="User Service is unavailable",
            )
        if response.is_error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="User Service rejected the internal request",
            )

        return UserServiceUser.model_validate(response.json())


user_service_client = UserServiceClient()
