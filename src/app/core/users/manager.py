import logging
import uuid
from typing import Optional

from fastapi import Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from pydantic import SecretStr

from app.core.config import get_config
from app.models.tables import User
from app.core.utils import send_account_verification_email, send_reset_password_email

config = get_config()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """
    A manager class for user-related operations.

    Attributes:
        reset_password_token_secret (SecretStr): The secret key for generating reset password tokens.
        reset_password_token_lifetime_seconds (int): The lifetime of reset password tokens in seconds.
        verification_token_secret (SecretStr): The secret key for generating verification tokens.
        verification_token_lifetime_seconds (int): The lifetime of verification tokens in seconds.

    Methods:
        async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
        ) -> None:
            Asynchronously executes tasks after a user requests to reset their password.

        async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
        ) -> None:
            Asynchronously executes tasks after a user requests account verification.
    """

    reset_password_token_secret: SecretStr = config.JWT_SECRET_KEY
    reset_password_token_lifetime_seconds: int = (
        config.RESET_PASSWORD_TOKEN_LIFETIME_SECONDS
    )
    verification_token_secret: SecretStr = config.JWT_SECRET_KEY
    verification_token_lifetime_seconds: int = config.VERIFY_TOKEN_LIFETIME_SECONDS

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ) -> None:
        """
        Asynchronously executes tasks after a user requests to reset their password.

        Args:
            user (User): The user for whom the password reset is requested.
            token (str): The token generated for resetting the password.
            request (Optional[Request]): The optional request object associated with the action.

        Returns:
            None
        """

        send_reset_password_email(email_to=user.email, token=token)
        logger.info("sent reset password email to %s", user.email)

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ) -> None:
        """
        Asynchronously executes tasks after a user requests account verification.

        Args:
            user (User): The user for whom the account verification is requested.
            token (str): The token generated for account verification.
            request (Optional[Request]): The optional request object associated with the action.

        Returns:
            None
        """

        send_account_verification_email(email_to=user.email, token=token)
        logger.info("sent account verification email to %s", user.email)
