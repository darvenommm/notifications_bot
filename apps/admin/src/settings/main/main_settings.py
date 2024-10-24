from ipaddress import IPv4Address

from pydantic import Field, IPvAnyAddress
from pydantic_settings import BaseSettings, SettingsConfigDict


class MainSettings(BaseSettings):
    server_host: IPvAnyAddress = Field(IPv4Address("0.0.0.0"), alias="SERVER_HOST")
    server_port: int = Field(9003, alias="SERVER_PORT", ge=0, le=65535)
    workers_count: int = Field(1, alias="WORKERS_COUNT", ge=1)

    admin_username: str = Field("admin", alias="ADMIN_USERNAME")
    admin_password: str = Field("super_puper_password", alias="ADMIN_PASSWORD")

    model_config = SettingsConfigDict(env_file="./envs/.main.env", env_file_encoding="utf-8")
