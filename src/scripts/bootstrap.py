import asyncio
import json
import logging
from typing import Final

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Session
from app.models.tables import Category, Priority

INITIAL_DATA_FILE_PATH: Final[str] = "src/scripts/data.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def initiate_data(session: AsyncSession) -> None:
    # Load initial data from the file
    with open(INITIAL_DATA_FILE_PATH, "r") as f:
        initial_data_dict: dict[str, list[str]] = json.load(f)

    # Initiate priorities
    initial_priorities_names: list[str] = initial_data_dict["priorities_names"]
    priorities_result = await session.execute(
        (select(Priority).filter(Priority.name.in_(initial_priorities_names)))
    )
    priorities_from_db: list[Priority] = priorities_result.scalars().all()

    # If there are no priorities in the database, add the initial priorities
    if not priorities_from_db:
        priorities: list[Priority] = [
            Priority(name=priority_name) for priority_name in initial_priorities_names
        ]
        session.add_all(priorities)

    # Initiate categories
    initial_categories_names: list[str] = initial_data_dict["categories_names"]
    categories_result = await session.execute(
        (select(Category).filter(Category.name.in_(initial_categories_names)))
    )
    categories_from_db: list[Category] = categories_result.scalars().all()

    # If there are no categories in the database, add the initial categories
    if not categories_from_db:
        categories: list[Category] = [
            Category(name=category_name, created_by_id=None)
            for category_name in initial_categories_names
        ]
        session.add_all(categories)

    # Commit the changes
    await session.commit()


async def main() -> None:
    logger.info("Creating initial data")
    async with Session() as session:
        await initiate_data(session)
    logger.info("Initial data created")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
