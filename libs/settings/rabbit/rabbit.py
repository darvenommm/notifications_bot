from pydantic import Field
from pydantic_settings import BaseSettings


class RabbitSettings(BaseSettings):
    host: str = Field(alias="RABBIT_HOST")
    port: int = Field(alias="RABBIT_PORT", ge=0, le=65535)
    username: str = Field(alias="RABBIT_USERNAME")
    password: str = Field(alias="RABBIT_PASSWORD")

    @property
    def rabbit_connection_string(self) -> str:
        return f"amqp://{self.username}:{self.password}@{self.host}:{self.port}"
