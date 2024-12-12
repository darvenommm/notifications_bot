from datetime import datetime, timedelta, timezone
from http import HTTPMethod, HTTPStatus

from fastapi import HTTPException, Response
from proxy.settings.proxy import ProxySettings
from pydantic import BaseModel

from libs.base_classes.controller import Controller


class RegisterDTO(BaseModel):
    username: str
    password: str


class AuthController(Controller):
    __proxy_settings: ProxySettings

    def __init__(self, proxy_settings: ProxySettings) -> None:
        super().__init__()
        self.__proxy_settings = proxy_settings

        self._router.add_api_route(
            endpoint=self.register,
            path="/auth",
            methods=[HTTPMethod.POST],
            status_code=HTTPStatus.NO_CONTENT,
        )

    def register(self, response: Response, register_data: RegisterDTO) -> None:
        is_correct_username = register_data.username == self.__proxy_settings.admin_username
        is_correct_password = register_data.password == self.__proxy_settings.admin_password

        if not (is_correct_username and is_correct_password):
            raise HTTPException(HTTPStatus.UNAUTHORIZED, "Incorrect username or password")

        expires = datetime.now(timezone.utc) + timedelta(weeks=1)
        response.set_cookie(
            "username",
            register_data.username,
            httponly=True,
            secure=True,
            samesite="none",
            expires=expires,
        )
        response.set_cookie(
            "password",
            register_data.password,
            httponly=True,
            secure=True,
            samesite="none",
            expires=expires,
        )
