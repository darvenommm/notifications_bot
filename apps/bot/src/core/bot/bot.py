from aiogram import Bot as AiogramBot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from typing import Iterable

from libs.base_classes.bot_router import BotRouter
from bot.src.settings import BotSettings


class Bot:
    __bot: AiogramBot
    __dispatcher: Dispatcher

    __bot_settings: BotSettings
    __routes: Iterable[BotRouter]

    def __init__(self, bot_settings: BotSettings, routes: Iterable[BotRouter]) -> None:
        self.__bot_settings = bot_settings
        self.__routes = routes
        self.__set_up()

    @property
    def bot(self) -> AiogramBot:
        return self.__bot

    @property
    def dispatcher(self) -> Dispatcher:
        return self.__dispatcher

    @property
    def bot_and_dispatcher(self) -> tuple[AiogramBot, Dispatcher]:
        return (self.bot, self.dispatcher)

    def __set_up(self) -> None:
        properties = DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2)
        bot = AiogramBot(self.__bot_settings.token, default=properties)
        self.__bot = bot

        dispatcher = Dispatcher()
        for router in self.__routes:
            dispatcher.include_router(router.router)
        self.__dispatcher = dispatcher
