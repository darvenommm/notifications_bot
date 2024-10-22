import pydantic
import pydantic_settings

for package in (pydantic, pydantic_settings):
    if package is None:
        raise RuntimeError("Not found pydantic or pydantic_settings package")

from pydantic import Field, IPvAnyAddress
from pydantic_settings import BaseSettings


class RabbitSettings(BaseSettings):
    rabbit_host: IPvAnyAddress = Field(alias="RABBIT_HOST")
    rabbit_port: int = Field(alias="RABBIT_PORT", ge=0, le=65535)
    rabbit_username: str = Field(alias="RABBIT_USERNAME")
    rabbit_password: str = Field(alias="RABBIT_PASSWORD")

    @property
    def rabbit_connection_string(self) -> str:
        return f"amqp://{self.rabbit_username}:{self.rabbit_password}@{self.rabbit_host}:{self.rabbit_port}"
