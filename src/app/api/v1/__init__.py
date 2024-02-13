from fastapi import APIRouter

from app.core.config import get_config

from .auth import router as auth_router
from .categories import router as categories_router
from .priorities import router as priorities_router
from .tasks import router as todos_router
from .users import router as users_router

config = get_config()

router = APIRouter(prefix=config.API_V1_STR)

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(priorities_router)
router.include_router(categories_router)
router.include_router(todos_router)
