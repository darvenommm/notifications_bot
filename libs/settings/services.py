from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServicesSettings(BaseSettings):
    users_url: HttpUrl = Field(alias="USERS_URL")
