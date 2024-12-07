from pydantic import Field, IPvAnyAddress
from pydantic_settings import BaseSettings


class ProxySettings(BaseSettings):
    host: IPvAnyAddress = Field(alias="PROXY_HOST")
    port: int = Field(alias="PROXY_PORT", ge=0, le=65535)

    admin_username: str = Field(alias="PROXY_ADMIN_USERNAME")
    admin_password: str = Field(alias="PROXY_ADMIN_PASSWORD")
