import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from typing import Iterable

from libs.base_classes.controller import Controller
from .settings.proxy import ProxySettings


class App:
    __proxy_settings: ProxySettings
    __controllers: Iterable[Controller]

    def __init__(self, proxy_settings: ProxySettings, controllers: Iterable[Controller]) -> None:
        self.__proxy_settings = proxy_settings
        self.__controllers = controllers

    def start(self) -> None:
        uvicorn.run(
            self.__get_set_server(),
            host=str(self.__proxy_settings.host),
            port=self.__proxy_settings.port,
        )

    def __get_set_server(self) -> FastAPI:
        server = FastAPI(default_response_class=ORJSONResponse, docs_url="/swagger")

        for controller in self.__controllers:
            server.include_router(controller.router)

        return server
