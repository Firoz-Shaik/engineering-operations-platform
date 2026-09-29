import secrets
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db


async def require_internal_api_key(
    api_key: str = Header(alias="X-Internal-API-Key"),
) -> None:
    if not secrets.compare_digest(api_key, settings.INTERNAL_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid internal service credentials",
        )


InternalService = Annotated[None, Depends(require_internal_api_key)]
DBSession = Annotated[AsyncSession, Depends(get_db)]