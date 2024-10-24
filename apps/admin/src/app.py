import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from typing import Iterable

from libs.base_classes.controller import Controller
from admin.src.settings import MainSettings


class App:
    __main_settings: MainSettings
    __controllers: Iterable[Controller]

    def __init__(self, main_settings: MainSettings, controllers: Iterable[Controller]) -> None:
        self.__main_settings = main_settings
        self.__controllers = controllers

    def start(self) -> None:
        uvicorn.run(
            self.__get_set_server(),
            host=str(self.__main_settings.server_host),
            port=self.__main_settings.server_port,
            workers=self.__main_settings.workers_count,
        )

    def __get_set_server(self) -> FastAPI:
        server = FastAPI(default_response_class=ORJSONResponse, docs_url="/swagger")

        for controller in self.__controllers:
            server.include_router(controller.router)

        return server
