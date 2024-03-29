import asyncio
from typing import Final

import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from app.core.database import engine, get_async_session
from app.main import app
from tests.conftest_utils import get_user_token_headers, insert_test_data


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_data():
    async with engine.begin() as conn:
        async with AsyncSession(conn, expire_on_commit=False) as async_session_:
            await insert_test_data(async_session_)


@pytest_asyncio.fixture(scope="session", autouse=True)
def event_loop():
    event_loop_policy = asyncio.get_event_loop_policy()
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture()
async def connection():
    async with engine.begin() as conn:
        yield conn
        await conn.rollback()


@pytest_asyncio.fixture()
async def async_session(connection: AsyncConnection):
    async with AsyncSession(connection, expire_on_commit=False) as async_session_:
        yield async_session_


@pytest_asyncio.fixture(autouse=True)
async def override_dependency(async_session: AsyncSession):
    app.dependency_overrides[get_async_session] = lambda: async_session


TEST_BASE_URL: Final[str] = "http://test"


@pytest_asyncio.fixture()
async def client():
    async with AsyncClient(app=app, base_url=TEST_BASE_URL) as ac, LifespanManager(app):
        yield ac


@pytest_asyncio.fixture()
async def user_token_headers(client: AsyncClient) -> dict[str, str]:
    return await get_user_token_headers(client)
