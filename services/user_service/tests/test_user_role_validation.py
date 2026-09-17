import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import Role
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate
from app.services.user_service import user_service


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        session.add_all([
            Role(name="superuser"),
            Role(name="admin"),
            Role(name="operator"),
            Role(name="developer"),
        ])
        await session.commit()
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_duplicate_email_rejected(db_session):
    payload = UserCreate(email="first@example.com", full_name="First User", password="secret123", roles=["admin"])

    await user_repository.create_user(db_session, obj_in=payload)

    with pytest.raises(HTTPException, match="already exists"):
        await user_repository.create_user(db_session, obj_in=payload)


@pytest.mark.asyncio
async def test_duplicate_role_assignment_rejected(db_session):
    payload = UserCreate(
        email="second@example.com",
        full_name="Second User",
        password="secret123",
        roles=["admin", "admin"],
    )

    with pytest.raises(HTTPException, match="cannot be assigned more than once"):
        await user_service.create_user(db_session, obj_in=payload)
