from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings


class ServicesSettings(BaseSettings):
    users_url: AnyHttpUrl = Field(alias="USERS_URL")
    notifications_url: AnyHttpUrl = Field(alias="NOTIFICATIONS_URL")
    frontend_url: AnyHttpUrl = Field(alias="FRONTEND_URL")
