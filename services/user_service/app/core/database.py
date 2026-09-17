# app/core/database.py
# Handles database connection and session management.

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from .config import settings

# Create the SQLAlchemy engine
# The pool_pre_ping argument ensures that the connection is alive before being used.
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

# Create a session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for our ORM models
Base = declarative_base()

# Dependency for getting a DB session in path operations
async def get_db():
    """
    FastAPI dependency that provides a SQLAlchemy database session per request.
    It ensures the session is always closed after the request is finished.
    """
    async with SessionLocal() as db:
        yield db
