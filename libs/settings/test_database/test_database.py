from pydantic import Field
from pydantic_settings import BaseSettings

from ..database import BaseDatabaseSettings


class TestDatabaseSettings(BaseDatabaseSettings, BaseSettings):
    host: str = Field(alias="TEST_DB_HOST")
    port: int = Field(alias="TEST_DB_PORT", ge=0, le=65535)
    username: str = Field(alias="TEST_DB_USERNAME")
    password: str = Field(alias="TEST_DB_PASSWORD")
    name: str = Field(alias="TEST_DB_NAME")

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
