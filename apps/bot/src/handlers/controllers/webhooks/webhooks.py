from http import HTTPMethod, HTTPStatus

from aiogram.types import Update
from bot.src.core.bots import BotSettings
from bot.src.handlers.controllers import Controller
from bot.src.settings.envs.webhooks import webhooks_settings as settings
from fastapi import HTTPException, Request


class WebhooksControllers(Controller):
    __SECRET_TOKEN_HEADER = "X-Telegram-Bot-Api-Secret-Token"

    __bot_settings: BotSettings

    def __init__(self, bot_settings: BotSettings) -> None:
        super().__init__()
        self._router.tags = ["webhooks"]
        self._router.add_api_route(
            settings.webhooks_root,
            self.__webhooks,
            methods=[HTTPMethod.POST],
            status_code=HTTPStatus.OK,
        )

        self.__bot_settings = bot_settings

    async def __webhooks(self, request: Request) -> None:
        if not (settings.webhooks_secret == request.headers.get(self.__SECRET_TOKEN_HEADER)):
            raise HTTPException(HTTPStatus.FORBIDDEN, detail="Incorrect secret token")

        (bot, dispatcher) = (self.__bot_settings.bot, self.__bot_settings.dispatcher)

        update_data = await request.json()
        await dispatcher.feed_webhook_update(bot, Update(**update_data))
