from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.models.user import User
from app.services.user_service import user_service
from fastapi import HTTPException, status
from datetime import timedelta


class AuthService:
    async def auth_user_for_token(
            self, db: AsyncSession, *, email: str, password: str
    ):
        user = await user_service.get_user_by_email(db, email=email)

        if not user:
            raise(HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            ))
        if not verify_password(password, user.hashed_password):
            raise(HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            ))
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.email, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}

auth_service = AuthService()