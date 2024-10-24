from fastapi import Request, HTTPException
from http import HTTPStatus

from admin.src.settings import MainSettings


class AuthMiddleware:
    __main_settings: MainSettings

    def __init__(self, main_settings: MainSettings) -> None:
        self.__main_settings = main_settings

    async def middleware(self, request: Request) -> None:
        username = request.cookies.get("username")
        password = request.cookies.get("password")

        if (username is None) or (password is None):
            raise HTTPException(HTTPStatus.UNAUTHORIZED, "Not set username or password in cookies")

        is_correct_username = username == self.__main_settings.admin_username
        is_correct_password = password == self.__main_settings.admin_password

        if (not is_correct_username) or (not is_correct_password):
            raise HTTPException(HTTPStatus.UNAUTHORIZED, "Not correct username or password")
