from libs.logger import Logger

from .core.bot_runners import BaseBotRunner


class App:
    __bot_runner: BaseBotRunner
    __logger: Logger

    def __init__(self, bot_runner: BaseBotRunner, logger: Logger) -> None:
        self.__bot_runner = bot_runner
        self.__logger = logger

    def start(self) -> None:
        self.__logger().info("Start bot")

        try:
            self.__bot_runner.start()
        except Exception as exception:  # noqa: PIE786
            self.__logger().error(f"App was stopped by this exception: {exception}")
