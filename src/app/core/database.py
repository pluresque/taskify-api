from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_config

config = get_config()
engine: AsyncEngine = create_async_engine(config.POSTGRES_URI, echo=True)
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, Any]:
    """
    Asynchronously generates an async session.

    Yields:
        AsyncSession: An asynchronous session object.
    """
    async with Session() as session:
        yield session
