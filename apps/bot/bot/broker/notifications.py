import asyncio
from msgpack.fallback import unpackb  # type: ignore[import-untyped]
from typing import Any

from libs.logger import Logger
from libs.message_brokers.rabbit import RabbitConnector
from libs.contracts.notifications import SendRequest, NOTIFICATIONS_QUEUE
from libs.metrics import RECEIVED_BROKER_MESSAGES_TOTAL
from bot.core.bot import Bot


class NotificationsConsumer:
    __stop_event: asyncio.Event

    __bot: Bot
    __connector: RabbitConnector
    __logger: Logger

    def __init__(self, bot: Bot, connector: RabbitConnector, logger: Logger) -> None:
        self.__bot = bot
        self.__connector = connector
        self.__logger = logger
        self.__stop_event = asyncio.Event()

    async def start(self) -> None:
        self.__logger().info("Start NotificationsConsumer")
        await self.__start_listening()

    def stop(self) -> None:
        self.__logger().info("Stop NotificationsConsumer")
        self.__stop_event.set()

    async def __start_listening(self) -> None:
        async with self.__connector.get_channel() as channel:
            queue = await channel.declare_queue(NOTIFICATIONS_QUEUE, durable=True)

            while not self.__stop_event.is_set():
                try:
                    async with queue.iterator(timeout=5) as messages_iterator:
                        async for message in messages_iterator:
                            async with message.process():
                                self.__logger().info(
                                    f"Processed messages from NotificationsConsumer {unpackb(message.body)}"
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

                                RECEIVED_BROKER_MESSAGES_TOTAL.labels(
                                    consumer="bot",
                                    provider="notifications",
                                    title="sended a notification to user",
                                ).inc()

                except TimeoutError:
                    pass

            self.__logger().debug("NotificationsConsumer really stopped")
