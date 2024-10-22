from aiogram.types import Update
from fastapi import HTTPException, Request
from http import HTTPMethod, HTTPStatus

from libs.base_classes.controller import Controller
from bot.src.core.bot import Bot
from bot.src.settings import WebhooksSettings


class WebhooksControllers(Controller):
    __SECRET_TOKEN_HEADER = "X-Telegram-Bot-Api-Secret-Token"

    __bot: Bot
    __webhooks_settings: WebhooksSettings

    def __init__(self, bot: Bot, webhooks_settings: WebhooksSettings) -> None:
        super().__init__()
        self.__bot = bot
        self.__webhooks_settings = webhooks_settings

        self._router.add_api_route(
            endpoint=self.webhooks,
            path="/webhooks",
            methods=[HTTPMethod.POST],
            status_code=HTTPStatus.OK,
        )

    async def webhooks(self, request: Request) -> None:
        secret = self.__webhooks_settings.secret

        if not (secret == request.headers.get(self.__SECRET_TOKEN_HEADER)):
            raise HTTPException(HTTPStatus.FORBIDDEN, detail="Incorrect secret token")

        (bot, dispatcher) = (self.__bot.bot, self.__bot.dispatcher)

        update_data = await request.json()
        await dispatcher.feed_webhook_update(bot, Update(**update_data))
