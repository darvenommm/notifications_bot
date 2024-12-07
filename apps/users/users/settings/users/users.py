from pydantic import Field, IPvAnyAddress
from pydantic_settings import BaseSettings


class UsersSettings(BaseSettings):
    host: IPvAnyAddress = Field(alias="USERS_HOST")
    port: int = Field(alias="USERS_PORT", ge=0, le=65535)
