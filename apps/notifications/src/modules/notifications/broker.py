from aio_pika import Message
from aio_pika.abc import AbstractChannel
from msgpack import packb  # type: ignore[import-untyped]

from libs.contracts.notifications import SendRequest, NOTIFICATIONS_EXCHANGE, NOTIFICATIONS_QUEUE
from libs.message_brokers.rabbit import RabbitConnector


class NotificationsPublisher:
    __is_set: bool = False

    __connector: RabbitConnector

    def __init__(self, connector: RabbitConnector) -> None:
        self.__connector = connector

    async def __declare(self, channel: AbstractChannel) -> None:
        exchange = await channel.declare_exchange(NOTIFICATIONS_EXCHANGE, durable=True)
        queue = await channel.declare_queue(NOTIFICATIONS_QUEUE, durable=True)
        await queue.bind(exchange, routing_key=NOTIFICATIONS_QUEUE)

    async def send(self, send_data: SendRequest) -> None:
        async with self.__connector.get_channel() as channel:
            if not self.__is_set:
                await self.__declare(channel)
                self.__is_set = True

            exchange = await channel.get_exchange(NOTIFICATIONS_EXCHANGE, ensure=True)
            message = Message(packb(send_data.model_dump()))
            await exchange.publish(message, routing_key=NOTIFICATIONS_QUEUE)
