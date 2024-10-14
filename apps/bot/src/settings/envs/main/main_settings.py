from enum import StrEnum
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotType(StrEnum):
    POLLING = "polling"
    WEBHOOKS = "webhooks"


class MainSettings(BaseSettings):
    bot_type: BotType = Field(BotType.POLLING, alias="BOT_TYPE")

    bot_token: str = Field(alias="BOT_TOKEN")

    model_config = SettingsConfigDict(
        env_file="envs/.main.env",
        env_file_encoding="utf-8",
    )


main_settings = MainSettings()
