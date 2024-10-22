import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from typing import AsyncContextManager, AsyncGenerator, Callable, Iterable

from libs.base_classes.controller import Controller
from .settings.main import MainSettings
from .modules.users import UsersUpdaterRPCClient


class App:
    __server: FastAPI

    __main_settings: MainSettings
    __users_updater: UsersUpdaterRPCClient
    __controllers: Iterable[Controller]

    def __init__(
        self,
        main_settings: MainSettings,
        users_updater: UsersUpdaterRPCClient,
        controllers: Iterable[Controller],
    ) -> None:
        self.__main_settings = main_settings
        self.__users_updater = users_updater
        self.__controllers = controllers
        self.__server = self.__get_set_server()

    def start(self) -> None:
        uvicorn.run(
            self.__server,
            host=str(self.__main_settings.server_host),
            port=self.__main_settings.server_port,
            workers=self.__main_settings.workers_count,
        )

    def __get_set_server(self) -> FastAPI:
        server = FastAPI(
            default_response_class=ORJSONResponse,
            docs_url="/swagger",
            lifespan=self.__get_lifespan(),
        )

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
