from typing import Iterable

from libs.logger import Logger
from libs.base_classes.controller import Controller
from bot.settings.bot import BotSettings
from bot.settings.webhooks import WebhooksSettings
from bot.core.bot import Bot
from bot.core.bot_runners import BaseBotRunner
from bot.broker import UsersUpdaterRPCServer, NotificationsConsumer


class WebhooksBotRunner(BaseBotRunner):
    __webhooks_settings: WebhooksSettings

    def __init__(
        self,
        bot: Bot,
        logger: Logger,
        controllers: Iterable[Controller],
        bot_settings: BotSettings,
        users_updater: UsersUpdaterRPCServer,
        notifications_consumer: NotificationsConsumer,
        webhooks_settings: WebhooksSettings,
    ) -> None:
        super().__init__(
            bot,
            logger,
            controllers,
            bot_settings,
            users_updater,
            notifications_consumer,
        )
        self.__webhooks_settings = webhooks_settings

    async def _before_running(self) -> None:
        await self._bot.bot.set_webhook(
            self.__webhooks_settings.endpoint,
            secret_token=self.__webhooks_settings.secret,
        )

    async def _before_ending(self) -> None:
        bot = self._bot.bot

        await bot.delete_webhook()
        await bot.session.close()
