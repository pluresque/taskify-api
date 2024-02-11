import uuid
from typing import Optional

from pydantic import BaseModel

from app.models.tables import Category
from app.schemas.base import BaseInDB


class CategoryCreate(BaseModel):
    name: str


class CategoryRead(CategoryCreate):
    id: int

    class Config:
        orm_mode = True


class CategoryInDB(BaseInDB, CategoryCreate):
    created_by_id: Optional[uuid.UUID]

    class Config(BaseInDB.Config):
        orm_model = Category
