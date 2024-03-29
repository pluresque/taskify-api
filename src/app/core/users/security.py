from typing import Final, Optional, Union

from fastapi_users.authentication import JWTStrategy
from fastapi_users.jwt import SecretType, generate_jwt

from app.core.config import get_config
from app.models.tables import User

config = get_config()

JWT_HASHING_ALGORITHM: Final[str] = "HS256"


class TodosJWTStrategy(JWTStrategy):
    """
    JWT authentication strategy for Todos.

    Attributes:
        None

    Methods:
        __init__(
            self,
            secret: SecretType,
            lifetime_seconds: Optional[int],
            token_audience: Optional[list[str]] = None,
            algorithm: str = JWT_HASHING_ALGORITHM,
            public_key: Optional[SecretType] = None,
        ):
            Initializes the TodosJWTStrategy instance.

        async def write_token(self, user: User) -> str:
            Asynchronously generates and returns a JWT token for the given user.

        def generate_jwt_data(self, user: User) -> dict[str, Union[str, list[str], bool]]:
            Generates JWT data based on the user.

    """

    def __init__(
        self,
        secret: SecretType,
        lifetime_seconds: Optional[int],
        token_audience: Optional[list[str]] = None,
        algorithm: str = JWT_HASHING_ALGORITHM,
        public_key: Optional[SecretType] = None,
    ):
        if token_audience is None:
            token_audience = ["fastapi-users:auth", "fastapi-users:verify"]
        super().__init__(
            secret=secret,
            lifetime_seconds=lifetime_seconds,
            token_audience=token_audience,
            algorithm=algorithm,
            public_key=public_key,
        )

    async def write_token(self, user: User) -> str:
        """
        Asynchronously generates and returns a JWT token for the given user.

        Args:
            user (User): The user for whom the JWT token is generated.

        Returns:
            str: The generated JWT token.

        """

        data = self.generate_jwt_data(user)
        return generate_jwt(
            data, self.encode_key, self.lifetime_seconds, algorithm=self.algorithm
        )

    def generate_jwt_data(self, user: User) -> dict[str, Union[str, list[str], bool]]:
        """
        Generates JWT data based on the given user.

        Args:
            user (User): The user for whom the JWT data is generated.

        Returns:
            dict[str, Union[str, list[str], bool]]: A dictionary containing JWT data including user ID, audience, email, and user status.

        """

        return dict(
            user_id=str(user.id),
            aud=self.token_audience,
            email=user.email,
            isSuperuser=user.is_superuser,
        )


def get_jwt_strategy() -> JWTStrategy:
    """
    Retrieves the JWT authentication strategy.

    Returns:
        JWTStrategy: The JWT authentication strategy instance.

    """
    return TodosJWTStrategy(
        secret=config.JWT_SECRET_KEY, lifetime_seconds=config.JWT_LIFETIME_SECONDS
    )
