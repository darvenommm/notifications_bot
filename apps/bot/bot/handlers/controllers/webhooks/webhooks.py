from http import HTTPMethod, HTTPStatus

from aiogram.types import Update
from bot.core.bot import Bot
from bot.settings.webhooks import WebhooksSettings
from fastapi import HTTPException, Request

from libs.base_classes.controller import Controller
from libs.logger import Logger


class WebhooksControllers(Controller):
    __SECRET_TOKEN_HEADER = "X-Telegram-Bot-Api-Secret-Token"

    __bot: Bot
    __webhooks_settings: WebhooksSettings
    __logger: Logger

    def __init__(self, bot: Bot, webhooks_settings: WebhooksSettings, logger: Logger) -> None:
        super().__init__()
        self.__bot = bot
        self.__webhooks_settings = webhooks_settings
        self.__logger = logger

        self._router.add_api_route(
            endpoint=self.webhooks,
            path="/webhooks",
            methods=[HTTPMethod.POST],
            status_code=HTTPStatus.OK,
        )

    async def webhooks(self, request: Request) -> None:
        self.__logger().info("Get data from telegram (webhoooks)")
        secret = self.__webhooks_settings.secret

        if secret != request.headers.get(self.__SECRET_TOKEN_HEADER):
            self.__logger().error("Incorrect a webhooks secret token")
            raise HTTPException(HTTPStatus.FORBIDDEN, detail="Incorrect secret token")

        (bot, dispatcher) = self.__bot.bot_and_dispatcher

        update_data = await request.json()
        await dispatcher.feed_webhook_update(bot, Update(**update_data))
