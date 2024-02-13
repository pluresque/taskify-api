from typing import Any, Optional, Type, TypeVar, Union

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dal.constants import GET_MULTI_DEFAULT_SKIP
from app.models.base import Base
from app.schemas.base import BaseInDB, BaseUpdateInDB

ModelType = TypeVar("ModelType", bound=Base)
InDBSchemaType = TypeVar("InDBSchemaType", bound=BaseInDB)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseUpdateInDB)


class DBRepo:
    """
    A repository class for interacting with the database asynchronously.

    Methods:
        __init__(self) -> None:
            Initializes the DBRepo class.

        async def get(
            self, session: AsyncSession,
            *, table_model: Type[ModelType], query_filter=None,
        ) -> Union[Optional[ModelType]]:
            Asynchronously retrieves a single record from the database based on the provided query.

        async def get_multi(
            self, session: AsyncSession,
            *, table_model: Type[ModelType],
            query_filter=None, skip: int = GET_MULTI_DEFAULT_SKIP,
            limit: Optional[int] = None,
        ) -> list[ModelType]:
            Asynchronously retrieves multiple records from the database based on the provided query conditions.

        async def create(
            self, session: AsyncSession, *, obj_to_create: InDBSchemaType
        ) -> ModelType:
            Asynchronously creates a new record in the database.

        async def update(
            self,
            session: AsyncSession,
            *,
            updated_obj: UpdateSchemaType,
            db_obj_to_update: Optional[ModelType] = None,
        ) -> Optional[ModelType]:
            Asynchronously updates an existing record in the database.

        async def delete(
            self, session: AsyncSession, *, table_model: Type[ModelType], id_to_delete: int
        ) -> None:
            Asynchronously deletes a record from the database based on the provided ID.
    """

    def __init__(self) -> None: ...

    async def get(
        self, session: AsyncSession, *,
        table_model: Type[ModelType], query_filter=None,
    ) -> Union[Optional[ModelType]]:
        """
        Asynchronously retrieves a single record from the database.

        Args:
            session (AsyncSession): The asynchronous database session.
            table_model (Type[ModelType]): The SQLAlchemy model representing the database table.
            query_filter (Optional[ClauseElement]): The filter criteria for the query (default: None).

        Returns:
            Union[Optional[ModelType]]: The retrieved record, if found; otherwise None.
        """

        query = select(table_model)
        if query_filter is not None:
            query = query.filter(query_filter)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_multi(
        self, session: AsyncSession, *, table_model: Type[ModelType],
        query_filter=None, skip: int = GET_MULTI_DEFAULT_SKIP,
        limit: Optional[int] = None,
    ) -> list[ModelType]:
        """
        Asynchronously retrieves multiple records from the database.

        Args:
            session (AsyncSession): The asynchronous database session.
            table_model (Type[ModelType]): The SQLAlchemy model representing the database table.
            query_filter (Optional[ClauseElement]): The filter criteria for the query (default: None).
            skip (int): The number of records to skip (default: GET_MULTI_DEFAULT_SKIP).
            limit (Optional[int]): The maximum number of records to retrieve (default: None).

        Returns:
            list[ModelType]: A list of retrieved records.
        """

        query = select(table_model)

        if query_filter is not None:
            query = query.filter(query_filter)
        query = query.offset(skip)

        if limit is not None:
            query = query.limit(limit)
        result = await session.execute(query)

        return result.scalars().all()

    async def create(
        self, session: AsyncSession, *, obj_to_create: InDBSchemaType
    ) -> ModelType:
        """
        Asynchronously creates a new record in the database.

        Args:
            session (AsyncSession): The asynchronous database session.
            obj_to_create (InDBSchemaType): The input schema representing the data to be created.

        Returns:
            ModelType: The created database object.
        """

        db_obj: ModelType = obj_to_create.to_orm()
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        *,
        updated_obj: UpdateSchemaType,
        db_obj_to_update: Optional[ModelType] = None,
    ) -> Optional[ModelType]:
        existing_obj_to_update: Optional[ModelType] = (
            db_obj_to_update
            or await self.get(
                session,
                table_model=updated_obj.Config.orm_model,
                query_filter=updated_obj.Config.orm_model.id == updated_obj.id,
            )
        )
        """
        Asynchronously updates an existing record in the database.

        Args:
            session (AsyncSession): The asynchronous database session.
            updated_obj (UpdateSchemaType): The updated schema representing the data to be updated.
            db_obj_to_update (Optional[ModelType]): The database object to be updated (default: None).

        Returns:
            Optional[ModelType]: The updated database object, if the update was successful; otherwise None.

        """

        if existing_obj_to_update:
            existing_obj_to_update_data = existing_obj_to_update.dict()
            updated_data: dict[str, Any] = updated_obj.to_orm().dict()
            for field in existing_obj_to_update_data:
                if field in updated_data:
                    setattr(existing_obj_to_update, field, updated_data[field])
            session.add(existing_obj_to_update)
            await session.commit()
            await session.refresh(existing_obj_to_update)
        return existing_obj_to_update

    async def delete(
        self, session: AsyncSession, *, table_model: Type[ModelType], id_to_delete: int
    ) -> None:
        """
        Asynchronously deletes a record from the database.

        Args:
            session (AsyncSession): The asynchronous database session.
            table_model (Type[ModelType]): The SQLAlchemy model representing the database table.
            id_to_delete (int): The ID of the record to be deleted.

        Returns:
            None
        """

        query = delete(table_model).where(table_model.id == id_to_delete)
        await session.execute(query)
        await session.commit()
