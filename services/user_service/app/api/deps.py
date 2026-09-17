from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.core import security
from app.core.database import get_db
from app.models.user import User
from app.schemas.token import TokenData
from app.services.user_service import user_service


# This defines the security scheme for getting a bearer token.
# tokenUrl points to the endpoint where the client can fetch a token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user_service/v1/auth/token")

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to get the current user from a JWT token.
    This will be used to protect endpoints.
    
    Raises:
        HTTPException: 401 Unauthorized if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.jwt.decode(
            token, security.settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except (JWTError, ValidationError):
        raise credentials_exception
        
    user = await user_service.get_user_by_email(db, email=token_data.email)
    if user is None or user.deleted_at is not None:
        raise credentials_exception
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]
DBSession = Annotated[AsyncSession, Depends(get_db)]


async def get_admin_user(current_user: CurrentUser) -> User:
    user_role_names = {
        user_role.role.name.lower()
        for user_role in current_user.user_roles
        if user_role.role is not None
    }
    if "admin" not in user_role_names and "superuser" not in user_role_names:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user

AdminUser = Annotated[User, Depends(get_admin_user)]