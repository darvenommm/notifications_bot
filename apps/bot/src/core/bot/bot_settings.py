from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from bot.src.settings.envs.main import main_settings
from bot.src.handlers.commands import commands_router


class BotSettings:
    __bot: Bot
    __dispatcher: Dispatcher

    def __init__(self) -> None:
        self.__init()

    @property
    def bot(self) -> Bot:
        return self.__bot

    @property
    def dispatcher(self) -> Dispatcher:
        return self.__dispatcher

    def __init(self) -> None:
        bot = Bot(
            token=main_settings.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2),
        )

        dispatcher = Dispatcher()
        dispatcher.include_router(commands_router)

        self.__bot = bot
        self.__dispatcher = dispatcher
