from typing import Any, AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy declarative models.

    Inherits from SQLAlchemy 2.0 DeclarativeBase to provide common functionality
    for all database models. All models should inherit from this class.
   """
    pass


async def get_session() -> AsyncGenerator[AsyncSession | Any, Any]:
    """FastAPI dependency that provides a database session.

    Creates a new async database session for each request and automatically
    closes it when the request is complete. Used as a dependency in route handlers.

    Yields:
        AsyncSession: An active database session for the current request context."""

    async with AsyncSessionLocal() as session:
        yield session
