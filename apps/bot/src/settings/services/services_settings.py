from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServicesSettings(BaseSettings):
    users_url: HttpUrl = Field(alias="USERS_URL")

    model_config = SettingsConfigDict(env_file="./envs/.services.env", env_file_encoding="utf-8")
