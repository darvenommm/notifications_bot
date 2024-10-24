from http import HTTPMethod, HTTPStatus
from fastapi import Response, HTTPException
from pydantic import BaseModel

from libs.base_classes.controller import Controller
from admin.src.settings import MainSettings


class RegisterDTO(BaseModel):
    username: str
    password: str


class AuthController(Controller):
    __main_settings: MainSettings

    def __init__(self, main_settings: MainSettings) -> None:
        super().__init__()
        self.__main_settings = main_settings

        self._router.add_api_route(
            endpoint=self.register,
            path="/auth",
            methods=[HTTPMethod.POST],
            status_code=HTTPStatus.NO_CONTENT,
        )

    def register(self, response: Response, register_data: RegisterDTO) -> None:
        is_correct_username = register_data.username == self.__main_settings.admin_username
        is_correct_password = register_data.password == self.__main_settings.admin_password

        if not (is_correct_username and is_correct_password):
            raise HTTPException(HTTPStatus.UNAUTHORIZED, "Incorrect username or password")

        response.set_cookie("username", self.__main_settings.admin_username)
        response.set_cookie("password", self.__main_settings.admin_password)
