import uuid
from typing import Optional

from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dal.constants import GET_MULTI_DEFAULT_LIMIT, GET_MULTI_DEFAULT_SKIP
from app.dal.db_repo import DBRepo
from app.core.exceptions import ResourceAlreadyExists, ResourceNotExists, UserNotAllowed
from app.models.tables import Category, Priority, Todo
from app.schemas import CategoryInDB, TodoInDB, TodoUpdateInDB


class DBService:
    """
    A service class for interacting with the database asynchronously.

    Attributes:
        None

    Methods:
        __init__(self) -> None:
            Initializes the DBService class.

        async def _validate_todo_categories(
            self,
            session: AsyncSession,
            *,
            todo_categories_ids: list[int],
            created_by_id: uuid.UUID,
        ) -> bool:
            Asynchronously validates todo categories against user and ensures no duplications.

        async def get_priorities(self, session: AsyncSession) -> list[Priority]:
            Asynchronously retrieves priorities from the database.

        async def get_categories(
            self,
            session: AsyncSession,
            *,
            created_by_id: uuid.UUID,
            skip: int = GET_MULTI_DEFAULT_SKIP,
            limit: int = GET_MULTI_DEFAULT_LIMIT,
        ) -> list[Category]:
            Asynchronously retrieves categories from the database based on the provided user ID.

        async def add_category(
            self, session: AsyncSession, *, category_in: CategoryInDB
        ) -> Category:
            Asynchronously adds a new category to the database.

        async def delete_category(
            self, session: AsyncSession, *, id_to_delete: int, created_by_id: uuid.UUID
        ) -> None:
            Asynchronously deletes a category from the database based on the provided ID and user ID.

        async def get_todos(
            self,
            session: AsyncSession,
            *,
            created_by_id: uuid.UUID,
            skip: int = GET_MULTI_DEFAULT_SKIP,
            limit: int = GET_MULTI_DEFAULT_LIMIT,
        ) -> list[Todo]:
            Asynchronously retrieves todos from the database based on the provided user ID.

        async def add_todo(self, session: AsyncSession, *, todo_in: TodoInDB) -> Todo:
            Asynchronously adds a new todo to the database after validating categories.

        async def update_todo(
            self, session: AsyncSession, *, updated_todo: TodoUpdateInDB
        ) -> Todo:
            Asynchronously updates an existing todo in the database after validating categories.

        async def delete_todo(
            self, session: AsyncSession, *, id_to_delete: int, created_by_id: uuid.UUID
        ) -> None:
            Asynchronously deletes a todo from the database based on the provided ID and user ID.

    """

    def __init__(self) -> None:
        self._repo = DBRepo()

    async def _validate_todo_categories(
        self,
        session: AsyncSession,
        *,
        todo_categories_ids: list[int],
        created_by_id: uuid.UUID,
    ) -> bool:
        """
        Validates that the todo categories are valid for the user and ensures no duplications.

        Args:
            session (AsyncSession): The async session to perform database operations.
            todo_categories_ids (list[int]): The list of todo category IDs to validate.
            created_by_id (uuid.UUID): The ID of the user who created the categories.

        Returns:
            bool: True if the todo categories are valid and contain no duplications, False otherwise.

        """

        # validates that the todo categories are valid to the user + no duplications
        default_categories_filter = Category.created_by_id.is_(None)
        user_categories_filter = Category.created_by_id == created_by_id
        valid_categories_filter = or_(default_categories_filter, user_categories_filter)
        todo_categories_ids_filter = Category.id.in_(todo_categories_ids)

        categories_from_db: list[Category] = await self._repo.get_multi(
            session,
            table_model=Category,
            query_filter=and_(valid_categories_filter, todo_categories_ids_filter),
        )
        are_categories_valid: bool = len(todo_categories_ids) == len(categories_from_db)
        return are_categories_valid

    async def get_priorities(self, session: AsyncSession) -> list[Priority]:
        """
        Retrieves a list of priorities from the database.

        Args:
            session (AsyncSession): The async session to perform database operations.

        Returns:
            list[Priority]: A list of Priority objects retrieved from the database.

        """

        return await self._repo.get_multi(session, table_model=Priority)

    async def get_categories(
        self,
        session: AsyncSession,
        *,
        created_by_id: uuid.UUID,
        skip: int = GET_MULTI_DEFAULT_SKIP,
        limit: int = GET_MULTI_DEFAULT_LIMIT,
    ) -> list[Category]:
        """
        Retrieves a list of categories from the database.

        Args:
            session (AsyncSession): The async session to perform database operations.
            created_by_id (uuid.UUID): The ID of the user who created the categories.
            skip (int, optional): Number of categories to skip. Defaults to GET_MULTI_DEFAULT_SKIP.
            limit (int, optional): Maximum number of categories to return. Defaults to GET_MULTI_DEFAULT_LIMIT.

        Returns:
            list[Category]: A list of Category objects retrieved from the database.

        """

        default_categories_filter = Category.created_by_id.is_(None)
        user_categories_filter = Category.created_by_id == created_by_id
        query_filter = or_(user_categories_filter, default_categories_filter)
        return await self._repo.get_multi(
            session,
            table_model=Category,
            query_filter=query_filter,
            limit=limit,
            skip=skip,
        )

    async def add_category(
        self, session: AsyncSession, *, category_in: CategoryInDB
    ) -> Category:
        users_categories: list[Category] = await self.get_categories(
            session, created_by_id=category_in.created_by_id
        )
        """
        Adds a new category to the database.

        Retrieves the categories created by the user specified in category_in.
        Checks if the category name already exists among the user's categories.
        If it exists, raises ResourceAlreadyExists exception.
        If not, creates the new category and returns it.

        Args:
            session (AsyncSession): The async session to perform database operations.
            category_in (CategoryInDB): The CategoryInDB object representing the category to add.

        Returns:
            Category: The newly created Category object.

        Raises:
            ResourceAlreadyExists: If the category name already exists among the user's categories.

        """

        users_categories_names: list[str] = [c.name for c in users_categories]
        if category_in.name in users_categories_names:
            raise ResourceAlreadyExists(resource="category name")
        return await self._repo.create(session, obj_to_create=category_in)

    async def delete_category(
        self, session: AsyncSession, *, id_to_delete: int, created_by_id: uuid.UUID
    ) -> None:
        category_to_delete: Optional[Category] = await self._repo.get(
            session, table_model=Category, query_filter=Category.id == id_to_delete
        )
        """
        Deletes a category from the database.

        Retrieves the category with the specified ID to delete.
        If the category does not exist, raises ResourceNotExists exception.
        If the category exists but was not created by the specified user, raises UserNotAllowed exception.
        If the category exists and was created by the specified user, deletes the category.

        Args:
            session (AsyncSession): The async session to perform database operations.
            id_to_delete (int): The ID of the category to delete.
            created_by_id (uuid.UUID): The ID of the user who created the category.

        Raises:
            ResourceNotExists: If the category with the specified ID does not exist.
            UserNotAllowed: If the category exists but was not created by the specified user.

        """

        if not category_to_delete:
            raise ResourceNotExists(resource="category")
        if category_to_delete.created_by_id != created_by_id:
            raise UserNotAllowed(
                "a user can not delete a category that was not created by him"
            )
        await self._repo.delete(
            session, table_model=Category, id_to_delete=id_to_delete
        )

    async def get_todos(
        self,
        session: AsyncSession,
        *,
        created_by_id: uuid.UUID,
        skip: int = GET_MULTI_DEFAULT_SKIP,
        limit: int = GET_MULTI_DEFAULT_LIMIT,
    ) -> list[Todo]:
        """
        Retrieves todos belonging to a specific user from the database.

        Retrieves todos with the specified user ID as the creator.
        Supports pagination by skipping a certain number of todos and limiting the number of todos returned.

        Args:
            session (AsyncSession): The async session to perform database operations.
            created_by_id (uuid.UUID): The ID of the user who created the todos.
            skip (int, optional): Number of todos to skip. Defaults to GET_MULTI_DEFAULT_SKIP.
            limit (int, optional): Maximum number of todos to return. Defaults to GET_MULTI_DEFAULT_LIMIT.

        Returns:
            list[Todo]: A list of Todo objects belonging to the specified user.

        """

        return await self._repo.get_multi(
            session,
            table_model=Todo,
            query_filter=Todo.created_by_id == created_by_id,
            skip=skip,
            limit=limit,
        )

    async def add_todo(self, session: AsyncSession, *, todo_in: TodoInDB) -> Todo:
        if await self._validate_todo_categories(
            session,
            todo_categories_ids=todo_in.categories_ids,
            created_by_id=todo_in.created_by_id,
        ):
            """
            Adds a new todo to the database.

            Validates todo categories to ensure they are valid for the user and not duplicated.
            If categories are valid, creates a new todo with the provided data.
            If the priority specified in the todo is not valid, raises a ValueError.
            If the categories specified in the todo are not valid, raises a ValueError.

            Args:
                session (AsyncSession): The async session to perform database operations.
                todo_in (TodoInDB): The data to create the new todo.

            Raises:
                ValueError: If the priority or categories specified in the todo are not valid.

            Returns:
                Todo: The newly created todo object.

            """

            try:
                return await self._repo.create(session, obj_to_create=todo_in)
            except IntegrityError:
                raise ValueError("priority is not valid")
        raise ValueError("categories are not valid")

    async def update_todo(
        self, session: AsyncSession, *, updated_todo: TodoUpdateInDB
    ) -> Todo:
        """
        Updates an existing todo in the database with new data.

        Retrieves the todo object to update based on the provided ID.
        Checks if the todo exists and if it was created by the same user attempting to update it.
        Validates the updated todo's categories to ensure they are valid for the user.
        If the categories are valid, updates the todo with the provided data.
        If the priority specified in the todo is not valid, raises a ValueError.
        If the categories specified in the todo are not valid, raises a ValueError.

        Args:
            session (AsyncSession): The async session to perform database operations.
            updated_todo (TodoUpdateInDB): The updated data for the todo.

        Raises:
            ResourceNotExists: If the todo to update does not exist.
            UserNotAllowed: If the user attempting to update the todo is not its creator.
            ValueError: If the priority or categories specified in the todo are not valid.

        Returns:
            Todo: The updated todo object.

        """

        todo_to_update: Optional[Todo] = await self._repo.get(
            session, table_model=Todo, query_filter=Todo.id == updated_todo.id
        )
        if not todo_to_update:
            raise ResourceNotExists(resource="todo")
        if not todo_to_update.created_by_id == updated_todo.created_by_id:
            raise UserNotAllowed(
                "a user can not update a todo that was not created by him"
            )
        if await self._validate_todo_categories(
            session,
            todo_categories_ids=updated_todo.categories_ids,
            created_by_id=updated_todo.created_by_id,
        ):
            try:
                todo_updated_obj: Optional[Todo] = await self._repo.update(
                    session, updated_obj=updated_todo, db_obj_to_update=todo_to_update
                )
                if todo_updated_obj:
                    return todo_updated_obj
                raise ResourceNotExists(resource="todo")
            except IntegrityError:
                raise ValueError("priority is not valid")
        raise ValueError("categories are not valid")

    async def delete_todo(
        self, session: AsyncSession, *, id_to_delete: int, created_by_id: uuid.UUID
    ) -> None:
        """
        Deletes a todo from the database.

        Retrieves the todo object to delete based on the provided ID.
        Checks if the todo exists and if it was created by the same user attempting to delete it.
        If the todo exists and was created by the user, deletes the todo from the database.

        Args:
            session (AsyncSession): The async session to perform database operations.
            id_to_delete (int): The ID of the todo to delete.
            created_by_id (uuid.UUID): The ID of the user who created the todo.

        Raises:
            ResourceNotExists: If the todo to delete does not exist.
            UserNotAllowed: If the user attempting to delete the todo is not its creator.

        """

        todo_to_delete: Optional[Todo] = await self._repo.get(
            session, table_model=Todo, query_filter=Todo.id == id_to_delete
        )
        if not todo_to_delete:
            raise ResourceNotExists(resource="todo")
        if todo_to_delete.created_by_id != created_by_id:
            raise UserNotAllowed(
                "a user can not delete a todo that was not created by him"
            )
        await self._repo.delete(session, table_model=Todo, id_to_delete=id_to_delete)


db_service = DBService()
