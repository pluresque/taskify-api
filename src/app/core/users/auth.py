from fastapi_users.authentication import AuthenticationBackend, BearerTransport

from app.core.config import get_config
from app.core.users.security import get_jwt_strategy

config = get_config()

bearer_transport = BearerTransport(tokenUrl=f"{config.API_V1_STR}/auth/login")
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
