import asyncio
import uvicorn
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncContextManager, AsyncGenerator, Callable, Iterable
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from libs.logger import Logger
from libs.base_classes.controller import Controller
from libs.metrics import RequestsMetricsMiddleware
from bot.settings.bot import BotSettings
from bot.core.bot import Bot
from bot.broker import UsersUpdaterRPCServer, NotificationsConsumer


class BaseBotRunner(ABC):
    _bot: Bot
    _logger: Logger
    _bot_settings: BotSettings
    __controllers: Iterable[Controller]
    __users_updater: UsersUpdaterRPCServer
    __notifications_consumer: NotificationsConsumer

    def __init__(
        self,
        bot: Bot,
        logger: Logger,
        controllers: Iterable[Controller],
        bot_settings: BotSettings,
        users_updater: UsersUpdaterRPCServer,
        notifications_consumer: NotificationsConsumer,
    ) -> None:
        self._bot = bot
        self._logger = logger
        self._bot_settings = bot_settings
        self.__controllers = controllers
        self.__users_updater = users_updater
        self.__notifications_consumer = notifications_consumer

    @abstractmethod
    async def _before_running(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def _before_ending(self) -> None:
        raise NotImplementedError()

    def start(self) -> None:
        self._logger().info("Start BaseBotRunner")
        uvicorn.run(
            self.__get_server(),
            host=str(self._bot_settings.host),
            port=self._bot_settings.port,
        )

    def __get_server(self) -> FastAPI:
        self._logger().info("Start creating a server in BaseBotRunner")
        server = FastAPI(
            lifespan=self.__get_lifespan(),
            default_response_class=ORJSONResponse,
            docs_url="/swagger",
        )

        server.add_middleware(RawContextMiddleware, plugins=[plugins.CorrelationIdPlugin()])

        RequestsMetricsMiddleware.set_server_name("bot")
        server.add_middleware(RequestsMetricsMiddleware)
        for controller in self.__controllers:
            server.include_router(controller.router)

        self._logger().info("End creating a server in BaseBotRunner")

        return server

    def __get_lifespan(self) -> Callable[[FastAPI], AsyncContextManager[None]]:
        self._logger().info("Get lifespan in BaseBotRunner")

        @asynccontextmanager
        async def lifespan(server: FastAPI) -> AsyncGenerator[None, None]:
            self._logger().debug("Before running bot")

            await self._before_running()

            users_updater_task = asyncio.create_task(self.__users_updater.start())
            notifications_consumer_task = asyncio.create_task(self.__notifications_consumer.start())

            self._logger().debug("Before run server: Tasks are set")

            yield

            self._logger().debug("After close server")

            self.__users_updater.stop()
            self.__notifications_consumer.stop()

            await asyncio.gather(
                users_updater_task,
                notifications_consumer_task,
                return_exceptions=True,
            )

            await self._before_ending()

            self._logger().debug("End webhooks server")

        return lifespan
