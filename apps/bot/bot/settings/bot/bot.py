from enum import StrEnum
from pydantic import Field
from pydantic_settings import BaseSettings


class BotRunningType(StrEnum):
    POLLING = "polling"
    WEBHOOKS = "webhooks"


class BotSettings(BaseSettings):
    type: BotRunningType = Field(alias="BOT_RUNNING_TYPE")
    token: str = Field(alias="BOT_TOKEN")
