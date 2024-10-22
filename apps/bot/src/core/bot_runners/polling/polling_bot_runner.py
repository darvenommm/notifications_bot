import asyncio
from signal import SIGINT, SIGTERM

from bot.src.core.bot import Bot
from bot.src.rpc import UsersUpdaterRPCServer
from ..base_bot_runner import BaseBotRunner


class PollingBotRunner(BaseBotRunner):
    __users_updater: UsersUpdaterRPCServer

    def __init__(self, bot: Bot, users_updater: UsersUpdaterRPCServer) -> None:
        super().__init__(bot)
        self.__users_updater = users_updater

    def _run(self) -> None:
        print("Start PollingBot")
        asyncio.run(self.__run_polling())

    def __add_stop_signals_handler(self) -> None:
        def stop_handler() -> None:
            self.__users_updater.stop()
            asyncio.create_task(self._bot.dispatcher.stop_polling())

        loop = asyncio.get_running_loop()
        for signal in (SIGINT, SIGTERM):
            loop.add_signal_handler(signal, stop_handler)

    async def __run_polling(self) -> None:
        print("run polling")

        self.__add_stop_signals_handler()

        bot, dispatcher = self._bot.bot_and_dispatcher

        async with asyncio.TaskGroup() as tasks_group:
            tasks_group.create_task(self.__users_updater.start())
            tasks_group.create_task(dispatcher.start_polling(bot, handle_signals=False))
