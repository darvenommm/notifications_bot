from aio_pika import Message, ExchangeType
from aio_pika.abc import AbstractChannel, HeadersType
from datetime import datetime
from msgpack import packb  # type: ignore[import-untyped]

from libs.contracts.notifications import (
    AddNotificationDTO,
    SendRequest,
    NOTIFICATIONS_EXCHANGE,
    NOTIFICATIONS_QUEUE,
)
from libs.message_brokers.rabbit import RabbitConnector


class NotificationsPublisher:
    __is_set: bool = False

    __connector: RabbitConnector

    def __init__(self, connector: RabbitConnector) -> None:
        self.__connector = connector

    async def __declare(self, channel: AbstractChannel) -> None:
        exchange = await channel.declare_exchange(
            NOTIFICATIONS_EXCHANGE,
            "x-delayed-message",
            durable=True,
            arguments={"x-delayed-type": ExchangeType.DIRECT.value},
        )
        queue = await channel.declare_queue(NOTIFICATIONS_QUEUE, durable=True)
        await queue.bind(exchange, routing_key=NOTIFICATIONS_QUEUE)

    async def send(self, send_data: SendRequest, datetime: datetime) -> None:
        async with self.__connector.get_channel() as channel:
            if not self.__is_set:
                await self.__declare(channel)
                self.__is_set = True

            exchange = await channel.get_exchange(NOTIFICATIONS_EXCHANGE, ensure=True)

            delay_ms = int((datetime.timestamp() - datetime.now().timestamp()) * 1000)
            print(delay_ms)
            headers: HeadersType = {"x-delay": max(delay_ms, 0)}
            message = Message(packb(send_data.model_dump()), headers=headers)

            await exchange.publish(message, routing_key=NOTIFICATIONS_QUEUE)
