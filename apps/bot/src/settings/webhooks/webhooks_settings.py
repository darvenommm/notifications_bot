from ipaddress import IPv4Address

from pydantic import Field, HttpUrl, IPvAnyAddress
from pydantic_settings import BaseSettings, SettingsConfigDict


class WebhooksSettings(BaseSettings):
    host: IPvAnyAddress = Field(IPv4Address("0.0.0.0"), alias="SERVER_HOST")
    port: int = Field(9000, alias="SERVER_PORT", ge=0, le=65535)
    outer_host: HttpUrl = Field(alias="OUTER_HOST")

    secret: str | None = Field(None, alias="WEBHOOKS_SECRET")
    workers_count: int = Field(1, alias="WORKERS_COUNT", ge=1)

    @property
    def url(self) -> str:
        return f"{str(self.outer_host).rstrip('/')}/webhooks"

    model_config = SettingsConfigDict(env_file="envs/.webhooks.env", env_file_encoding="utf-8")
