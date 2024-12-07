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
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def db_connection_sync_string(self) -> str:
        return f"postgresql+psycopg://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"
