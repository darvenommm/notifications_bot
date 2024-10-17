from ipaddress import IPv4Address

from pydantic import Field, IPvAnyAddress
from pydantic_settings import BaseSettings


class MainSettings(BaseSettings):
    server_host: IPvAnyAddress = Field(IPv4Address("0.0.0.0"), alias="SERVER_HOST")
    server_port: int = Field(9001, alias="SERVER_PORT", ge=0, le=65535)
    workers_count: int = Field(1, alias="WORKERS_COUNT", ge=1)

    db_host: IPvAnyAddress = Field(alias="DB_HOST")
    db_port: int = Field(alias="DB_PORT", ge=0, le=65535)
    db_username: str = Field(alias="DB_USERNAME")
    db_password: str = Field(alias="DB_PASSWORD")
    db_name: str = Field(alias="DB_NAME")
    db_schema: str = Field(alias="DB_SCHEMA")

    queue_host: IPvAnyAddress = Field(alias="QUEUE_HOST")
    queue_port: int = Field(alias="QUEUE_PORT", ge=0, le=65535)
    queue_username: str = Field(alias="QUEUE_USERNAME")
    queue_password: str = Field(alias="QUEUE_PASSWORD")

    @property
    def db_connection_string(self) -> str:
        """Use asyncpg engine."""

        return f"postgresql+asyncpg://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}"

    @property
    def db_connection_sync_string(self) -> str:
        """Use psycopg engine."""

        return f"postgresql+psycopg://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}"

    @property
    def queue_connection_string(self) -> str:
        return f"amqp://{self.queue_username}:{self.queue_password}@{self.queue_host}:{self.queue_port}"


main_settings = MainSettings()
