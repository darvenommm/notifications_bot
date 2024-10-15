from .core.bots import BaseBot


class App:
    __bot: BaseBot

    def __init__(self, bot: BaseBot) -> None:
        self.__bot = bot

    @property
    def bot(self) -> BaseBot:
        return self.__bot

    def start(self) -> None:
        self.bot.start()
