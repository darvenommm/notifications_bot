from pydantic import Field, IPvAnyAddress
from pydantic_settings import BaseSettings


class NotificationsSettings(BaseSettings):
    host: IPvAnyAddress = Field(alias="NOTIFICATIONS_HOST")
    port: int = Field(alias="NOTIFICATIONS_PORT", ge=0, le=65535)
