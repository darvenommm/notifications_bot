import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from typing import Iterable

from libs.base_classes.controller import Controller
from libs.metrics import RequestsMetricsMiddleware
from .settings.notifications import NotificationsSettings


class App:
    __notifications_settings: NotificationsSettings
    __controllers: Iterable[Controller]

    def __init__(
        self,
        notifications_settings: NotificationsSettings,
        controllers: Iterable[Controller],
    ) -> None:
        self.__notifications_settings = notifications_settings
        self.__controllers = controllers

    def start(self) -> None:
        uvicorn.run(
            self.__get_set_server(),
            host=str(self.__notifications_settings.host),
            port=self.__notifications_settings.port,
        )

    def __get_set_server(self) -> FastAPI:
        server = FastAPI(default_response_class=ORJSONResponse, docs_url="/swagger")

        RequestsMetricsMiddleware.set_server_name("notifications")
        server.add_middleware(RequestsMetricsMiddleware)

        for controller in self.__controllers:
            server.include_router(controller.router)

        return server
