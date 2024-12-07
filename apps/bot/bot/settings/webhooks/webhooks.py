from pydantic import Field, HttpUrl, IPvAnyAddress
from pydantic_settings import BaseSettings


class WebhooksSettings(BaseSettings):
    host: IPvAnyAddress = Field(alias="BOT_HOST")
    port: int = Field(alias="BOT_PORT", ge=0, le=65535)
    outer_host: HttpUrl = Field(alias="BOT_OUTER_HOST")

    secret: str | None = Field(..., alias="WEBHOOKS_SECRET")

    @property
    def endpoint(self) -> str:
        return f"{str(self.outer_host).rstrip('/')}/webhooks"
