from .core.bot_runners import BaseBotRunner


class App:
    __bot_runner: BaseBotRunner

    def __init__(self, bot_runner: BaseBotRunner) -> None:
        self.__bot_runner = bot_runner

    def start(self) -> None:
        self.__bot_runner.start()
