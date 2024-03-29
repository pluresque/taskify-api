from fastapi import APIRouter, Depends, status
from pydantic import conint
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.dal import (
    GET_MULTI_DEFAULT_LIMIT,
    GET_MULTI_DEFAULT_SKIP,
    MAX_POSTGRES_INTEGER,
    db_service,
)
from app.models.tables import Category, User
from app.schemas import CategoryCreate, CategoryInDB, CategoryRead
from app.core.users.users import current_logged_user
from app.core.utils import (
    exception_handler,
    get_open_api_response,
    get_open_api_unauthorized_access_response,
)

router = APIRouter(
    prefix="/categories",
    dependencies=[Depends(current_logged_user), Depends(get_async_session)],
    tags=["Categories"],
)


@router.get(
    "",
    response_model=list[CategoryRead],
    responses={
        status.HTTP_401_UNAUTHORIZED: get_open_api_unauthorized_access_response()
    },
)
async def get_categories(
    skip: conint(ge=0, le=MAX_POSTGRES_INTEGER) = GET_MULTI_DEFAULT_SKIP,  # type: ignore[valid-type]
    limit: conint(ge=0, le=MAX_POSTGRES_INTEGER) = GET_MULTI_DEFAULT_LIMIT,  # type: ignore[valid-type]
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_logged_user),
) -> list[Category]:
    """
    Asynchronously retrieves categories from the database based on user ID.

    Args:
        skip (int): The number of records to skip (default: GET_MULTI_DEFAULT_SKIP).
        limit (int): The maximum number of records to return (default: GET_MULTI_DEFAULT_LIMIT).
        session (AsyncSession): The asynchronous database session (default: Depends(get_async_session)).
        user (User): The current logged-in user (default: Depends(current_logged_user)).

    Returns:
        list[Category]: A list of category objects.
    """

    return await db_service.get_categories(
        session, created_by_id=user.id, skip=skip, limit=limit
    )


@router.post(
    "", response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: get_open_api_unauthorized_access_response(),
        status.HTTP_400_BAD_REQUEST: get_open_api_response(
            {"Trying to add an existing category": "category name already exists"}
        ),
    },
)
@exception_handler
async def add_category(
    category_in: CategoryCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_logged_user),
) -> Category:
    """
    Asynchronously adds a new category to the database.

    Args:
        category_in (CategoryCreate): The input data for creating a new category.
        session (AsyncSession): The asynchronous database session (default: Depends(get_async_session)).
        user (User): The current logged-in user (default: Depends(current_logged_user)).

    Returns:
        Category: The newly created category object.

    Raises:
        HTTPException: If an error occurs during category addition.
    """
    category_in = CategoryInDB(name=category_in.name, created_by_id=user.id)
    return await db_service.add_category(session, category_in=category_in)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: get_open_api_unauthorized_access_response(),
        status.HTTP_403_FORBIDDEN: get_open_api_response(
            {
                "Trying to delete system or another users category": "a user can not delete a category that was not created by him"
            }
        ),
        status.HTTP_404_NOT_FOUND: get_open_api_response(
            {"Trying to delete non existing category": "category does not exists"}
        ),
    },
)
@exception_handler
async def delete_category(
    category_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_logged_user),
) -> None:
    await db_service.delete_category(
        session, id_to_delete=category_id, created_by_id=user.id
    )
