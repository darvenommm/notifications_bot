from ipaddress import IPv4Address
from pydantic import Field, IPvAnyAddress, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class WebhooksSettings(BaseSettings):
    server_host: IPvAnyAddress = Field(IPv4Address("0.0.0.0"), alias="SERVER_HOST")
    server_port: int = Field(9000, alias="SERVER_PORT", ge=0, le=65535)
    outer_host: HttpUrl = Field(alias="OUTER_HOST")

    webhooks_root: str = Field("/webhooks", alias="WEBHOOKS_ROOT", pattern="^/.+$")
    webhooks_secret: str | None = Field(None, alias="WEBHOOKS_SECRET")
    workers_count: int = Field(1, alias="WORKERS_COUNT", ge=1)

    @property
    def webhooks_url(self) -> str:
        return f"{str(self.outer_host).rstrip('/')}/{self.webhooks_root.lstrip('/')}"

    model_config = SettingsConfigDict(
        env_file="envs/.webhooks.env",
        env_file_encoding="utf-8",
    )


webhooks_settings = WebhooksSettings()
