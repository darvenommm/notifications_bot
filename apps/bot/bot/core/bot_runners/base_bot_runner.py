from abc import ABC, abstractmethod

from libs.logger import Logger
from bot.core.bot import Bot


class BaseBotRunner(ABC):
    _bot: Bot
    _logger: Logger

    def __init__(self, bot: Bot, logger: Logger) -> None:
        self._logger = logger
        self._bot = bot

    def start(self) -> None:
        self._logger().info("Run BaseBotRunner")
        self._run()

    @abstractmethod
    def _run(self) -> None:
        raise NotImplementedError("BaseBotRunner")
