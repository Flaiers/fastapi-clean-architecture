import os
from typing import Any, Dict, List, Union

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


def get_env_file(env_dir):
    if os.getenv("LEVEL") == "debug":
        env_dir.format("example.env")
    else:
        env_dir.format(".env")
    return env_dir


class Settings(BaseSettings):

    API: str = "/api"
    ADMIN: str = "/admin"
    STARTUP: str = "startup"
    SECRET_KEY: str
    FLASK_ADMIN_SWATCH: str = "cerulean"

    PROJECT_NAME: str = "FastAPI"
    DESCRIPTION: str = "FastAPI clean architecture"

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]  # noqa: N805
    ) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(
        cls, v: str | None, variables: Dict[str, Any]  # noqa: N805
    ) -> str:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=variables.get("DB_USER"),
            password=variables.get("DB_PASSWORD"),
            host=variables.get("DB_HOST"),
            port=variables.get("DB_PORT"),
            path="{0}".format(variables.get("DB_NAME"))
        )

    class Config(object):
        case_sensitive = True
        env_file = get_env_file("env/{0}")


settings = Settings()
