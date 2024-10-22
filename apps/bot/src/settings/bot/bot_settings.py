from enum import StrEnum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotType(StrEnum):
    POLLING = "polling"
    WEBHOOKS = "webhooks"


class BotSettings(BaseSettings):
    type: BotType = Field(BotType.POLLING, alias="BOT_TYPE")
    token: str = Field(alias="BOT_TOKEN")

    model_config = SettingsConfigDict(env_file="envs/.bot.env", env_file_encoding="utf-8")
