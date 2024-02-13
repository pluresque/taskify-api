from typing import Union

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import RelationshipProperty, relationship

from app.models.base import Base


class User(SQLAlchemyBaseUserTableUUID, Base): ...


class Priority(Base):
    """
    Represents a priority level item.

    Attributes:
        id (BigInteger): The unique identifier of the priority.
        name (str): The name of the priority level.

    """

    id = Column(BigInteger(), primary_key=True, autoincrement=True)
    name = Column(String(15), nullable=False, unique=True)


class Category(Base):
    """
    Represents a category item.

    Attributes:
        id (BigInteger): The unique identifier of the category.
        name (str): The name of the category.
        created_by_id (GUID): The ID of the user who created the category.

    Relationships:
        todos (list[Todo]): The todos associated with the category.

    """

    id = Column(BigInteger(), primary_key=True, autoincrement=True)
    name = Column(Text(), nullable=False)
    created_by_id = Column(GUID, ForeignKey("user.id"))

    __table_args__ = (
        UniqueConstraint("name", "created_by_id", name="unique_category"),
    )

    todos: RelationshipProperty = relationship(
        "Todo", secondary="todo_category", back_populates="categories", viewonly=True
    )


class Todo(Base):
    """
     Represents a Todo item.

     Attributes:
         id (BigInteger): The unique identifier of the todo.
         is_completed (bool): Indicates whether the todo is completed or not.
         content (str): The content of the todo.
         created_by_id (GUID): The ID of the user who created the todo.
         priority_id (BigInteger): The ID of the priority associated with the todo.

     Relationships:
         priority (Priority): The priority associated with the todo.
         categories (list[Category]): The categories associated with the todo.
         todos_categories (list[TodoCategory]): The todo-category relationships.

     Methods:
         dict(self) -> dict: Converts the object into a dictionary.

     """

    id = Column(BigInteger(), primary_key=True, autoincrement=True)
    is_completed = Column(Boolean(), nullable=False, default=False)
    content = Column(Text(), nullable=False)
    created_by_id = Column(GUID, ForeignKey("user.id"), nullable=False)
    priority_id = Column(BigInteger(), ForeignKey("priority.id"), nullable=False)

    priority: RelationshipProperty = relationship("Priority", lazy="selectin")
    categories: RelationshipProperty = relationship(
        "Category",
        secondary="todo_category",
        back_populates="todos",
        lazy="selectin",
        viewonly=True,
    )

    todos_categories: RelationshipProperty = relationship(
        "TodoCategory", lazy="selectin", cascade="all, delete-orphan"
    )

    def dict(self) -> dict:
        # adding todos_categories field to dict()
        # just update usage only
        todo_dict: dict[str, Union[int, str, bool]] = super().dict()
        todo_dict["todos_categories"] = self.todos_categories  # type: ignore[assignment]
        return todo_dict


class TodoCategory(Base):
    """
    Represents the relationship between Todos and Categories.

    Attributes:
        todo_id (BigInteger): The ID of the todo.
        category_id (BigInteger): The ID of the category.

    """

    todo_id = Column(
        BigInteger(), ForeignKey("todo.id", ondelete="CASCADE"), primary_key=True
    )
    category_id = Column(
        BigInteger(), ForeignKey("category.id", ondelete="CASCADE"), primary_key=True
    )
