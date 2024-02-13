import uuid
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.models.tables import User
from app.core.users.auth import auth_backend
from app.core.users.manager import UserManager


async def get_user_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase, User]:
    """
    Asynchronously retrieves the user database.

    Args:
        session (AsyncSession): The asynchronous database session (default: Depends(get_async_session)).

    Yields:
        AsyncGenerator[SQLAlchemyUserDatabase, User]: An asynchronous generator yielding the SQLAlchemy user database
        instance and the User model.

    """
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, Any]:
    """
    Asynchronously retrieves the user manager.

    Args:
        user_db (SQLAlchemyUserDatabase): The user database (default: Depends(get_user_db)).

    Yields:
        AsyncGenerator[UserManager, Any]: An asynchronous generator yielding the UserManager instance.

    """
    yield UserManager(user_db)


fast_api_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_logged_user = fast_api_users.current_user(
    active=True, verified=False, superuser=False
)
