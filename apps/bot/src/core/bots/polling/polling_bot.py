import asyncio

from bot.src.core.bots import BaseBot


class PollingBot(BaseBot):
    def _run(self) -> None:
        print("Start PollingBot")
        asyncio.run(self.__run_polling())

    async def __run_polling(self) -> None:
        (bot, dispatcher) = (self._bot_settings.bot, self._bot_settings.dispatcher)

        await dispatcher.start_polling(bot)
