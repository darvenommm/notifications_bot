from ipaddress import IPv4Address
from pydantic import Field, AnyHttpUrl
from pydantic_settings import BaseSettings


class ServicesSettings(BaseSettings):
    users_url: AnyHttpUrl = Field(alias="USERS_URL")
    notifications_url: AnyHttpUrl = Field(alias="NOTIFICATIONS_URL")