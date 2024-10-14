from abc import ABC, abstractmethod

from .bot_settings import BotSettings


class BaseBot(ABC):
    _bot_settings: BotSettings

    def __init__(self, bot_settings: BotSettings):
        self._bot_settings = bot_settings

    def start(self) -> None:
        print("Run BaseBot")
        self._run()

    @abstractmethod
    def _run(self) -> None:
        error_message = "Template method _run in BaseBot is not implemented"

        raise NotImplementedError(error_message)
