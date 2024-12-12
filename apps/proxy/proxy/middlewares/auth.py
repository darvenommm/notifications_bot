from http import HTTPStatus

from fastapi import HTTPException, Request
from proxy.settings.proxy import ProxySettings


class AuthMiddleware:
    __proxy_settings: ProxySettings

    def __init__(self, proxy_settings: ProxySettings) -> None:
        self.__proxy_settings = proxy_settings

    async def middleware(self, request: Request) -> None:
        username = request.cookies.get("username")
        password = request.cookies.get("password")

        if (username is None) or (password is None):
            raise HTTPException(HTTPStatus.UNAUTHORIZED, "Not set username or password in cookies")

        is_correct_username = username == self.__proxy_settings.admin_username
        is_correct_password = password == self.__proxy_settings.admin_password

        if (not is_correct_username) or (not is_correct_password):
            raise HTTPException(HTTPStatus.UNAUTHORIZED, "Not correct username or password")
