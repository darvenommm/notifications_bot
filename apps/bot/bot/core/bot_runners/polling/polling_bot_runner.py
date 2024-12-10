import asyncio

from bot.core.bot_runners import BaseBotRunner


class PollingBotRunner(BaseBotRunner):
    async def _before_running(self) -> None:
        (bot, dispatcher) = self._bot.bot_and_dispatcher
        asyncio.create_task(dispatcher.start_polling(bot, handle_signals=False))

    async def _before_ending(self) -> None:
        await self._bot.dispatcher.stop_polling()
