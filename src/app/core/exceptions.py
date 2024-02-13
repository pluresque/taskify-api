from dataclasses import dataclass
from typing import Any, Literal


@dataclass()
class APIError(Exception):
    """
    Represents an API error.

    Attributes:
        code (int): The error code.
        message (str): The error message.
        data (Any): Additional data associated with the error.

    """

    code: int = 500
    message: str = "Unknown error"
    data: Any = None


@dataclass
class ResourceAlreadyExists(APIError):
    code: Literal[409]
    message: str = "Resource already exists"


@dataclass
class ResourceNotExists(APIError):
    code: Literal[404]
    message: str = "Resource does not exist"


@dataclass
class UserNotAllowed(APIError):
    code: Literal[403]
    message: str = "User not allowed"
