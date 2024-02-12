from fastapi import APIRouter

from app.schemas import UserCreate, UserRead
from app.core.users.auth import auth_backend
from app.core.users.users import fast_api_users

router = APIRouter(prefix="/auth", tags=["Authorization"])


router.include_router(fast_api_users.get_register_router(UserRead, UserCreate))
router.include_router(fast_api_users.get_auth_router(auth_backend))
router.include_router(fast_api_users.get_reset_password_router())
router.include_router(fast_api_users.get_verify_router(UserRead))
