import asyncio
from msgpack.fallback import unpackb  # type: ignore[import-untyped]
from typing import Any

from libs.message_brokers.rabbit import RabbitConnector
from libs.contracts.notifications import SendRequest, NOTIFICATIONS_QUEUE
from bot.src.core.bot import Bot


class NotificationsConsumer:
    __stop_event: asyncio.Event

    __connector: RabbitConnector
    __bot: Bot

    def __init__(self, bot: Bot, connector: RabbitConnector) -> None:
        self.__bot = bot
        self.__connector = connector
        self.__stop_event = asyncio.Event()

    async def start(self) -> None:
        await self.__start_listening()

    def stop(self) -> None:
        print("Stop NotificationsConsumer")
        self.__stop_event.set()

    async def __start_listening(self) -> None:
        async with self.__connector.get_channel() as channel:
            queue = await channel.declare_queue(NOTIFICATIONS_QUEUE, durable=True)

            while not self.__stop_event.is_set():
                try:
                    async with queue.iterator(timeout=1) as messages_iterator:
                        async for message in messages_iterator:
                            async with message.process():
                                print(
                                    "processed messages from NotificationsConsumer",
                                    unpackb(message.body),
                                )

                                if self.__stop_event.is_set():
                                    await message.nack()
                                    break

                                request_payload: dict[str, Any] = unpackb(message.body)
                                request = SendRequest(
                                    reply_to=request_payload["reply_to"],
                                    message=request_payload["message"],
                                )

                                await self.__bot.bot.send_message(request.reply_to, request.message)

                except TimeoutError:
                    pass

            print("NotificationsConsumer really stopped")
