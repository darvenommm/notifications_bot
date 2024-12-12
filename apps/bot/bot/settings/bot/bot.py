from enum import StrEnum

from pydantic import Field, IPvAnyAddress
from pydantic_settings import BaseSettings


class BotRunningType(StrEnum):
    POLLING = "polling"
    WEBHOOKS = "webhooks"


class BotSettings(BaseSettings):
    type: BotRunningType = Field(alias="BOT_RUNNING_TYPE")
    token: str = Field(alias="BOT_TOKEN")
    host: IPvAnyAddress = Field(alias="BOT_HOST")
    port: int = Field(alias="BOT_PORT", ge=0, le=65535)
