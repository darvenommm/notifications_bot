import asyncio
import uvicorn
from contextlib import asynccontextmanager
from typing import AsyncContextManager, AsyncGenerator, Callable, Iterable
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from libs.base_classes.controller import Controller
from ..base_bot_runner import BaseBotRunner
from bot.src.core.bot import Bot
from bot.src.rpc import UsersUpdaterRPCServer
from bot.src.settings import WebhooksSettings


class WebhooksBotRunner(BaseBotRunner):
    __users_updater: UsersUpdaterRPCServer
    __webhooks_settings: WebhooksSettings
    __controllers: Iterable[Controller]

    def __init__(
        self,
        bot: Bot,
        users_updater: UsersUpdaterRPCServer,
        webhooks_settings: WebhooksSettings,
        controllers: Iterable[Controller],
    ):
        super().__init__(bot)
        self.__users_updater = users_updater
        self.__webhooks_settings = webhooks_settings
        self.__controllers = controllers

    def _run(self) -> None:
        print("Run WebhooksBot")
        uvicorn.run(
            self.__get_server(),
            host=str(self.__webhooks_settings.host),
            port=self.__webhooks_settings.port,
            workers=self.__webhooks_settings.workers_count,
        )

    def __get_server(self) -> FastAPI:
        server = FastAPI(
            lifespan=self.__get_lifespan(),
            default_response_class=ORJSONResponse,
            docs_url="/swagger",
        )

        for controller in self.__controllers:
            print(controller)
            server.include_router(controller.router)

        return server

    def __get_lifespan(self) -> Callable[[FastAPI], AsyncContextManager[None]]:
        @asynccontextmanager
        async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
            bot = self._bot.bot

            await bot.set_webhook(
                self.__webhooks_settings.url,
                secret_token=self.__webhooks_settings.secret,
            )
            users_updating_task = asyncio.create_task(self.__users_updater.start())

            yield

            try:
                users_updating_task.cancel()
                await users_updating_task
            except asyncio.CancelledError:
                print("Stop webhooks bot")

            await bot.delete_webhook()
            await bot.session.close()

        return lifespan