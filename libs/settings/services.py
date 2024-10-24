from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings


class ServicesSettings(BaseSettings):
    users_url: HttpUrl = Field(alias="USERS_URL")
    notifications_url: HttpUrl = Field(alias="NOTIFICATIONS_URL")
