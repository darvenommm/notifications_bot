from aiogram.filters import CommandStart

from libs.base_classes.bot_router import BotRouter
from .start import StartHandler


class CommandsRouter(BotRouter):
    def __init__(self) -> None:
        super().__init__()
        self._router.message(CommandStart())(StartHandler)
