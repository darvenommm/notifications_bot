import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from typing import AsyncContextManager, AsyncGenerator, Callable, Iterable

from libs.base_classes.controller import Controller
from libs.metrics import RequestsMetricsMiddleware
from .settings.users import UsersSettings
from .modules.users import UsersUpdaterRPCClient


class App:
    __server: FastAPI

    __users_settings: UsersSettings
    __users_updater: UsersUpdaterRPCClient
    __controllers: Iterable[Controller]

    def __init__(
        self,
        users_settings: UsersSettings,
        users_updater: UsersUpdaterRPCClient,
        controllers: Iterable[Controller],
    ) -> None:
        self.__users_settings = users_settings
        self.__users_updater = users_updater
        self.__controllers = controllers
        self.__server = self.__get_set_server()

    def start(self) -> None:
        uvicorn.run(
            self.__server,
            host=str(self.__users_settings.host),
            port=self.__users_settings.port,
        )

    def __get_set_server(self) -> FastAPI:
        server = FastAPI(
            default_response_class=ORJSONResponse,
            docs_url="/swagger",
            lifespan=self.__get_lifespan(),
        )

        RequestsMetricsMiddleware.set_server_name("users")
        server.add_middleware(RequestsMetricsMiddleware)

        for controller in self.__controllers:
            server.include_router(controller.router)

        return server

    def __get_lifespan(self) -> Callable[[FastAPI], AsyncContextManager[None]]:
        @asynccontextmanager
        async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
            users_updater_task = await self.__users_updater.start()

            yield

            self.__users_updater.stop()
            await users_updater_task

        return lifespan
