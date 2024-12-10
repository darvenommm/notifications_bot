from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings


class WebhooksSettings(BaseSettings):
    outer_host: HttpUrl = Field(alias="BOT_OUTER_HOST")
    secret: str | None = Field(..., alias="WEBHOOKS_SECRET")

    @property
    def endpoint(self) -> str:
        return f"{str(self.outer_host).rstrip('/')}/webhooks"
