from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator

from typing import List, Union, Dict, Any

import os


__all__ = ["settings"]


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
        cls, v: str | None, values: Dict[str, Any]  # noqa: N805
    ) -> str:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            port=values.get("DB_PORT"),
            path="{0}".format(values.get("DB_NAME"))
        )

    class Config:
        case_sensitive = True
        env_file = "env/{0}"

        if os.getenv("LEVEL") == "debug":  # noqa: WPS604
            env_file.format("example.env")
        else:
            env_file.format(".env")


settings = Settings()
