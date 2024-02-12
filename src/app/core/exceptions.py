from dataclasses import dataclass
from typing import Any, Literal


@dataclass(kw_only=True)
class APIError(Exception):
    code: int
    message: str
    data: Any


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
