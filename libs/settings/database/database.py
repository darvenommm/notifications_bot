from abc import ABC, abstractmethod

from pydantic import Field
from pydantic_settings import BaseSettings


class BaseDatabaseSettings(ABC):
    @property
    @abstractmethod
    def db_connection_string(self) -> str:
        """Use asyncpg engine."""

        raise NotImplementedError()

    @property
    @abstractmethod
    def db_connection_sync_string(self) -> str:
        """Use psycopg engine."""

        raise NotImplementedError()


class DatabaseSettings(BaseDatabaseSettings, BaseSettings):
    host: str = Field(alias="DB_HOST")
    port: int = Field(alias="DB_PORT", ge=0, le=65535)
    username: str = Field(alias="DB_USERNAME")
    password: str = Field(alias="DB_PASSWORD")
    database: str = Field(alias="DB_NAME")
    db_schema: str = Field(alias="DB_SCHEMA")

    @property
    def db_connection_string(self) -> str:
        username_data = f"{self.username}:{self.password}"
        host_data = f"{self.host}:{self.port}"

        return f"postgresql+asyncpg://{username_data}@{host_data}/{self.database}"

    @property
    def db_connection_sync_string(self) -> str:
        username_data = f"{self.username}:{self.password}"
        host_data = f"{self.host}:{self.port}"

        return f"postgresql+psycopg://{username_data}@{host_data}/{self.database}"
