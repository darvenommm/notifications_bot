import asyncio
import uvicorn
from contextlib import asynccontextmanager
from typing import AsyncContextManager, AsyncGenerator, Callable, Iterable
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from libs.logger import Logger
from libs.base_classes.controller import Controller
from bot.settings.webhooks import WebhooksSettings
from bot.core.bot import Bot
from bot.core.bot_runners import BaseBotRunner
from bot.broker import UsersUpdaterRPCServer, NotificationsConsumer


class WebhooksBotRunner(BaseBotRunner):
    __users_updater: UsersUpdaterRPCServer
    __notifications_consumer: NotificationsConsumer
    __webhooks_settings: WebhooksSettings
    __controllers: Iterable[Controller]

    def __init__(
        self,
        bot: Bot,
        logger: Logger,
        users_updater: UsersUpdaterRPCServer,
        notifications_consumer: NotificationsConsumer,
        webhooks_settings: WebhooksSettings,
        controllers: Iterable[Controller],
    ):
        super().__init__(bot, logger)
        self.__users_updater = users_updater
        self.__notifications_consumer = notifications_consumer
        self.__webhooks_settings = webhooks_settings
        self.__controllers = controllers

    def _run(self) -> None:
        self._logger().info("Run WebhooksBot")
        uvicorn.run(
            self.__get_server(),
            host=str(self.__webhooks_settings.host),
            port=self.__webhooks_settings.port,
        )

    def __get_server(self) -> FastAPI:
        self._logger().debug("Start creating a server in WebhooksBot")
        server = FastAPI(
            lifespan=self.__get_lifespan(),
            default_response_class=ORJSONResponse,
            docs_url="/swagger",
        )

        for controller in self.__controllers:
            server.include_router(controller.router)

        server.add_middleware(RawContextMiddleware, plugins=[plugins.CorrelationIdPlugin()])

        self._logger().debug("End creating a server in WebhooksBot")

        return server

    def __get_lifespan(self) -> Callable[[FastAPI], AsyncContextManager[None]]:
        self._logger().info("Get lifespan for server")

        @asynccontextmanager
        async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
            self._logger().debug("Before run webhooks server")
            bot = self._bot.bot

            await bot.set_webhook(
                self.__webhooks_settings.endpoint,
                secret_token=self.__webhooks_settings.secret,
            )

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

            await bot.delete_webhook()
            await bot.session.close()

            self._logger().debug("End webhooks server")

        return lifespan
