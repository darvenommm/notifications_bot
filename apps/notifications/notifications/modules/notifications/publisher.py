from datetime import datetime
from typing import Any

from aio_pika import ExchangeType, Message
from aio_pika.abc import AbstractChannel
from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from msgpack import packb

from libs.contracts.notifications import (
    AddNotificationDTO,
    SendRequest,
    NOTIFICATIONS_EXCHANGE,
    NOTIFICATIONS_QUEUE,
)
from libs.contracts.users import GetPaginationDTO
from libs.message_brokers.rabbit import RabbitConnector
from libs.metrics import SENDED_BROKER_MESSAGES_TOTAL
from libs.settings.services import ServicesSettings


class NotificationsPublisher:
    __is_set: bool = False

    __connector: RabbitConnector
    __services_settings: ServicesSettings
    __scheduler: AsyncIOScheduler

    def __init__(
        self,
        connector: RabbitConnector,
        services_settings: ServicesSettings,
    ) -> None:
        self.__connector = connector
        self.__services_settings = services_settings
        self.__scheduler = AsyncIOScheduler()

    async def __declare(self, channel: AbstractChannel) -> None:
        exchange = await channel.declare_exchange(
            NOTIFICATIONS_EXCHANGE,
            ExchangeType.DIRECT,
            durable=True,
        )
        queue = await channel.declare_queue(NOTIFICATIONS_QUEUE, durable=True)
        await queue.bind(exchange, routing_key=NOTIFICATIONS_QUEUE)

    def schedule_notification(self, notification_data: AddNotificationDTO) -> None:
        if not self.__scheduler.running:
            self.__scheduler.start()

        self.__scheduler.add_job(
            self.__send_to_users,
            trigger=DateTrigger(run_date=notification_data.datetime),
            args=(notification_data.message,),
        )

    async def __send_to_users(self, message: str) -> None:
        path = f"{self.__services_settings.users_url}users"

        async with ClientSession() as session:
            cursor: datetime | None = datetime.min
            while cursor is not None:
                params: dict[str, Any] = {"cursor": cursor.isoformat(), "limit": 20}

                async with session.get(path, params=params) as response:
                    response_data: dict[str, Any] = await response.json()
                    pagination_info = GetPaginationDTO(
                        users=response_data["users"],
                        cursor=response_data["cursor"],
                        pages_count=response_data["pages_count"],
                    )
                    cursor = pagination_info.cursor

                for user in pagination_info.users:
                    await self.__send_to_user(
                        SendRequest(reply_to=user.user_id, message=message),
                    )

    async def __send_to_user(self, send_data: SendRequest) -> None:
        async with self.__connector.get_channel() as channel:
            if not self.__is_set:
                await self.__declare(channel)
                self.__is_set = True

            exchange = await channel.get_exchange(NOTIFICATIONS_EXCHANGE, ensure=True)
            message = Message(packb(send_data.model_dump()))

            await exchange.publish(message, routing_key=NOTIFICATIONS_QUEUE)

            SENDED_BROKER_MESSAGES_TOTAL.labels(
                provider="notifications",
                consumer="bot",
                title="send notifications to user",
            ).inc()
