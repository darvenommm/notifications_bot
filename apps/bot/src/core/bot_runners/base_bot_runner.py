from abc import ABC, abstractmethod

from bot.src.core.bot import Bot


class BaseBotRunner(ABC):
    _bot: Bot

    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    def start(self) -> None:
        print("Run BaseBotRunner")
        self._run()

    @abstractmethod
    def _run(self) -> None:
        raise NotImplementedError()
