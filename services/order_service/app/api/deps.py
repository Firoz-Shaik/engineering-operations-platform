from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, Field, ValidationError

from app.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.USER_SERVICE_TOKEN_URL)


class TokenUser(BaseModel):
    id: UUID
    email: EmailStr
    roles: list[str] = Field(default_factory=list)


def decode_token(token: str) -> TokenUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        subject = payload.get("sub")
        if not isinstance(subject, str):
            raise credentials_exception
        return TokenUser.model_validate(
            {
                "id": subject,
                "email": payload.get("email"),
                "roles": payload.get("roles", []),
            }
        )
    except (JWTError, ValidationError):
        raise credentials_exception from None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenUser:
    return decode_token(token)


CurrentUser = Annotated[TokenUser, Depends(get_current_user)]
