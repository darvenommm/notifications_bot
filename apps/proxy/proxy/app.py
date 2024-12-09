import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Iterable

from libs.settings.services import ServicesSettings
from libs.base_classes.controller import Controller
from .settings.proxy import ProxySettings


class App:
    __proxy_settings: ProxySettings
    __services_settings: ServicesSettings
    __controllers: Iterable[Controller]

    def __init__(
        self,
        proxy_settings: ProxySettings,
        services_settings: ServicesSettings,
        controllers: Iterable[Controller],
    ) -> None:
        self.__proxy_settings = proxy_settings
        self.__services_settings = services_settings
        self.__controllers = controllers

    def start(self) -> None:
        uvicorn.run(
            self.__get_set_server(),
            host=str(self.__proxy_settings.host),
            port=self.__proxy_settings.port,
        )

    def __get_set_server(self) -> FastAPI:
        server = FastAPI(default_response_class=ORJSONResponse, docs_url="/swagger")

        server.add_middleware(
            CORSMiddleware,
            allow_origins=[str(self.__services_settings.frontend_url).rstrip("/")],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        for controller in self.__controllers:
            server.include_router(controller.router)

        return server
