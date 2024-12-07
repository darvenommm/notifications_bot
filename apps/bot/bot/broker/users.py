import asyncio
from aio_pika import Message
from aio_pika.abc import AbstractChannel, AbstractIncomingMessage
from msgpack import packb  # type: ignore[import-untyped]
from msgpack.fallback import unpackb  # type: ignore[import-untyped]
from typing import Any, cast
from uuid import uuid4

from libs.logger import Logger
from libs.message_brokers.rabbit import RabbitConnector
from libs.contracts.users import UpdateRequest, UpdateResponse, USERS_QUEUE
from bot.core.bot import Bot


class UsersUpdaterRPCServer:
    __bot: Bot
    __connector: RabbitConnector
    __logger: Logger

    __stop_event: asyncio.Event

    def __init__(self, bot: Bot, connector: RabbitConnector, logger: Logger) -> None:
        self.__bot = bot
        self.__connector = connector
        self.__logger = logger
        self.__stop_event = asyncio.Event()

    def stop(self) -> None:
        self.__logger().info("Stop UsersUpdaterRPCServer")
        self.__stop_event.set()

    async def start(self) -> None:
        self.__logger().info("Start UsersUpdaterRPCServer")
        async with self.__connector.get_channel() as channel:
            users_queue = await channel.declare_queue(USERS_QUEUE, durable=True)

            while not self.__stop_event.is_set():
                try:
                    async with users_queue.iterator(timeout=5) as messages_iterator:
                        async for message in messages_iterator:
                            if self.__stop_event.is_set():
                                break

                            await self.__handle_message(message, channel)
                except TimeoutError:
                    pass

        self.__logger().debug("UsersUpdaterRPCServer really closed")

    async def __handle_message(
        self,
        message: AbstractIncomingMessage,
        channel: AbstractChannel,
    ) -> None:
        async with message.process():
            self.__logger().info(f"Message in UsersUpdaterRPCServer {unpackb(message.body)}")
            reply_to, correlation_id = (message.reply_to, message.correlation_id)

            if (reply_to is None) or (correlation_id is None):
                await message.nack(requeue=False)
                return

            request_data: dict[str, Any] = unpackb(message.body)
            request_payload = UpdateRequest(user_id=cast(int, request_data["user_id"]))

            user_data = await self.__bot.bot.get_chat(request_payload.user_id, request_timeout=30)
            response = UpdateResponse(
                user_id=user_data.id,
                full_name=user_data.full_name,
                username=user_data.username,
            )
            response_message = Message(
                packb(response.model_dump()),
                correlation_id=correlation_id,
                message_id=(message.message_id or str(uuid4())),
            )

            self.__logger().info(f"Response message in UsersUpdaterRPCServer {response_message}")

            await channel.default_exchange.publish(response_message, reply_to)
