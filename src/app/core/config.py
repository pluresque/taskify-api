from functools import lru_cache
from typing import Any, Optional

from pydantic import (
    AnyHttpUrl,
    BaseSettings,
    EmailStr,
    PostgresDsn,
    SecretStr,
    validator,
)


class Settings(BaseSettings):
    """
    Settings for the Taskify API.

    Attributes:
        PROJECT_NAME (str): The name of the project.
        API_V1_STR (str): The base URL path for API version 1.
        JWT_SECRET_KEY (SecretStr): The secret key for JSON Web Token (JWT) encoding.
        JWT_LIFETIME_SECONDS (int): The lifetime of JWT tokens in seconds.
        CORS_ORIGINS (list): List of allowed CORS origins.
        POSTGRES_DB (str): The name of the PostgreSQL database.
        POSTGRES_HOST (str): The hostname of the PostgreSQL database server.
        POSTGRES_USER (str): The username for PostgreSQL authentication.
        POSTGRES_PASSWORD (SecretStr): The password for PostgreSQL authentication.
        POSTGRES_URI (Optional[PostgresDsn]): The connection URI for PostgreSQL.
        SMTP_TLS (bool): Whether to use TLS for SMTP.
        SMTP_HOST (Optional[str]): The hostname of the SMTP server.
        SMTP_PORT (Optional[int]): The port of the SMTP server.
        SMTP_USER (Optional[str]): The username for SMTP authentication.
        SMTP_PASSWORD (Optional[SecretStr]): The password for SMTP authentication.
        EMAILS_FROM_EMAIL (Optional[EmailStr]): The sender's email address for outgoing emails.
        EMAILS_FROM_NAME (Optional[str]): The sender's name for outgoing emails.
        EMAIL_TEMPLATES_DIR (str): The directory path for email templates.
        EMAILS_ENABLED (bool): Whether outgoing emails are enabled.
        RESET_PASSWORD_TOKEN_LIFETIME_SECONDS (int): The lifetime of reset password tokens in seconds.
        VERIFY_TOKEN_LIFETIME_SECONDS (int): The lifetime of verification tokens in seconds.
        FRONT_END_BASE_URL (AnyHttpUrl): The base URL of the front-end application.

    Methods:
        assemble_db_connection(cls, _: str, values: dict[str, Any]) -> str:
            Assemble the database connection URI.
        get_project_name(cls, v: Optional[str], values: dict[str, Any]) -> str:
            Get the project name for emails.
        get_emails_enabled(cls, _: bool, values: dict[str, Any]) -> bool:
            Check if emails are enabled based on SMTP configuration.
        parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            Parse environment variables for configuration fields.

    """

    PROJECT_NAME: str = "Taskify API"
    API_V1_STR: str = "/api/v1"
    JWT_SECRET_KEY: SecretStr

    # 60 seconds by 60 minutes (1 hour) and then by 12 (for 12 hours total)
    JWT_LIFETIME_SECONDS: int = 60 * 60 * 12

    # CORS_ORIGINS is a string of ';' separated origins.
    # e.g:  'http://localhost:8080;http://localhost:3000'
    CORS_ORIGINS: list[AnyHttpUrl]

    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_URI: Optional[PostgresDsn] = None

    @validator("POSTGRES_URI", pre=True)
    def assemble_db_connection(cls, _: str, values: dict[str, Any]) -> str:
        """
        Pre-validation method for assembling the PostgreSQL database connection URI.

        Args:
            cls: The class object.
            _: str: Unused parameter.
            values (dict[str, Any]): The values dictionary containing POSTGRES_* attributes.

        Returns:
            str: The assembled PostgreSQL database connection URI.

        """

        postgres_password: SecretStr = values.get("POSTGRES_PASSWORD", SecretStr(""))
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=postgres_password.get_secret_value(),
            host=values.get("POSTGRES_HOST"),
            path=f'/{values.get("POSTGRES_DB")}',
        )

    SMTP_TLS: bool = True
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[SecretStr] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: dict[str, Any]) -> str:
        """
        Validator method for obtaining the project name to be used in emails.

        Args:
            cls: The class object.
            v (Optional[str]): The value of EMAILS_FROM_NAME.
            values (dict[str, Any]): The values dictionary containing PROJECT_NAME.

        Returns:
            str: The project name to be used in emails.

        """

        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAIL_TEMPLATES_DIR: str = "./src/assets/"
    EMAILS_ENABLED: bool = False

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, _: bool, values: dict[str, Any]) -> bool:
        """
        Pre-validation method for determining if email functionality is enabled.

        Args:
            cls: The class object.
            _: bool: Unused parameter.
            values (dict[str, Any]): The values dictionary containing SMTP_HOST, SMTP_PORT, and EMAILS_FROM_EMAIL.

        Returns:
            bool: True if email functionality is enabled, False otherwise.

        """

        return all(
            [
                values.get("SMTP_HOST"),
                values.get("SMTP_PORT"),
                values.get("EMAILS_FROM_EMAIL"),
            ]
        )

    # 60 seconds by 60 minutes (1 hour) and then by 12 (for 12 hours total)
    RESET_PASSWORD_TOKEN_LIFETIME_SECONDS: int = 60 * 60 * 12
    VERIFY_TOKEN_LIFETIME_SECONDS: int = 60 * 60 * 12

    FRONT_END_BASE_URL: AnyHttpUrl

    class Config:
        """
        Configuration class for settings.

        Attributes:
            env_file (str): The name of the environment file.
            case_sensitive (bool): Indicates whether settings are case-sensitive.

        Methods:
            @classmethod
            def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
                Parses and returns the value of an environment variable based on its field name.

        """

        env_file = ".env"
        case_sensitive = True

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            """
            Parses and returns the value of an environment variable based on its field name.

            Args:
                cls: The class object.
                field_name (str): The name of the environment variable.
                raw_val (str): The raw value of the environment variable.

            Returns:
                Any: The parsed value of the environment variable.

            """

            if field_name == "CORS_ORIGINS":
                return [origin for origin in raw_val.split(";")]
            # The following line is ignored by mypy because:
            # error: Type'[Config]' has no attribute 'json_loads',
            # even though it is like the documentation: https://docs.pydantic.dev/latest/usage/settings/
            return cls.json_loads(raw_val)  # type: ignore[attr-defined]


@lru_cache()
def get_config() -> Settings:
    """
    Retrieves the settings configuration.

    Returns:
        Settings: The settings configuration.

    """

    return Settings()
