"""
app/core/security.py

Security utilities for:
- Password hashing/verification
- JWT token creation/verification helpers

This module is imported as `from app.core import security` in a few places,
so it also re-exports `jwt`, `settings`, and `ALGORITHM` for convenience.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import jwt

from app.core.config import settings

# JWT settings
ALGORITHM = settings.ALGORITHM


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        raise ValueError("Password must be at most 72 bytes when encoded as UTF-8")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    `subject` is stored in the 'sub' claim (we use email).
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode: dict[str, Any] = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


