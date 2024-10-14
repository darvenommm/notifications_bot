import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from typing import AsyncGenerator, Callable, Iterable

from bot.src.core.bot import BaseBot, BotSettings
from bot.src.settings.envs.webhooks import webhooks_settings
from bot.src.handlers.controllers import Controller


class WebhooksBot(BaseBot):
    __controllers: Iterable[Controller]

    def __init__(self, bot_settings: BotSettings, controllers: Iterable[Controller]):
        super().__init__(bot_settings)
        self.__controllers = controllers

    def _run(self) -> None:
        print("Run WebhooksBot")
        uvicorn.run(
            self.server,
            host=str(webhooks_settings.server_host),
            port=webhooks_settings.server_port,
            workers=webhooks_settings.workers_count,
        )

    @property
    def server(self) -> FastAPI:
        server = FastAPI(
            lifespan=self.get_lifespan(),
            default_response_class=ORJSONResponse,
            docs_url="/swagger",
        )

        for controller in self.__controllers:
            server.include_router(controller.router)

        return server

    def get_lifespan(self) -> Callable[[], AsyncGenerator[None, None]]:
        @asynccontextmanager
        async def lifespan(_) -> AsyncGenerator[None, None]:
            bot = self._bot_settings.bot

            await bot.set_webhook(
                webhooks_settings.webhooks_url,
                secret_token=webhooks_settings.webhooks_secret,
            )
            yield
            await bot.delete_webhook()
            await bot.session.close()

        return lifespan
