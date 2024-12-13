import asyncio
from contextlib import suppress
from datetime import datetime
from typing import Any, cast
from uuid import uuid4

from aio_pika import Message
from aio_pika.abc import AbstractChannel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from msgpack import packb
from msgpack.fallback import unpackb

from libs.contracts.users import USERS_EXCHANGE, USERS_QUEUE, UpdateRequest, UpdateResponse
from libs.logger import Logger
from libs.message_brokers.rabbit import RabbitConnector
from libs.metrics import RECEIVED_BROKER_MESSAGES_TOTAL, SENDED_BROKER_MESSAGES_TOTAL

from .repository import UsersRepository


class UsersUpdaterRPCClient:
    __channel: AbstractChannel | None = None
    __callbacks_queue_name: str | None = None
    __scheduler: AsyncIOScheduler
    __stop_event: asyncio.Event
    __correlation_id: str = str(uuid4())

    __connector: RabbitConnector
    __users_repository: UsersRepository
    __logger: Logger

    def __init__(
        self,
        connector: RabbitConnector,
        users_repository: UsersRepository,
        logger: Logger,
    ) -> None:
        self.__connector = connector
        self.__users_repository = users_repository
        self.__scheduler = AsyncIOScheduler()
        self.__stop_event = asyncio.Event()
        self.__logger = logger

    async def start(self) -> asyncio.Task[None]:
        self.__logger().info("start users updater")
        async with self.__connector.get_channel() as channel:
            self.__channel = channel

            await self.__declare()
            self.__set_scheduler()
            return asyncio.create_task(self.__start_listening_callbacks_queue())

    def stop(self) -> None:
        self.__logger().info("Stop UsersUpdaterRPCClient")
        self.__stop_event.set()
        self.__scheduler.shutdown()
        self.__clean()

    async def __declare(self) -> None:
        session = self.__get_channel()

        users_exchange = await session.declare_exchange(USERS_EXCHANGE, durable=True)
        users_queue = await session.declare_queue(USERS_QUEUE, durable=True)
        await users_queue.bind(users_exchange, routing_key=USERS_QUEUE)

        callbacks_queue = await session.declare_queue(exclusive=True)
        self.__callbacks_queue_name = callbacks_queue.name

    async def __job(self) -> None:
        self.__logger().info("start jobbing")
        session = self.__get_channel()
        users_exchange = await session.get_exchange(USERS_EXCHANGE, ensure=True)

        cursor: datetime | None = datetime.min
        while cursor is not None:
            users = await self.__users_repository.get_page(cursor=cursor, limit=20)
            cursor = None if len(users) == 0 else users[-1].created_at

            for user in users:
                self.__logger().info(f"processing user: {user.user_id=}")
                payload: bytes = packb(UpdateRequest(user_id=user.user_id).model_dump())
                message = Message(
                    payload,
                    message_id=str(uuid4()),
                    reply_to=self.__get_callbacks_queue(),
                    correlation_id=self.__correlation_id,
                )
                await users_exchange.publish(message, USERS_QUEUE)

                SENDED_BROKER_MESSAGES_TOTAL.labels(
                    provider="users", consumer="bot", title="send request for update user data"
                ).inc()

    def __set_scheduler(self) -> None:
        self.__logger().info("set schedular")
        self.__scheduler.add_job(self.__job, "interval", minutes=1)
        self.__scheduler.start()

    async def __start_listening_callbacks_queue(self) -> None:
        self.__logger().info("start listening")
        session = self.__get_channel()
        callbacks_queue = await session.get_queue(self.__get_callbacks_queue())

        while not self.__stop_event.is_set():
            with suppress(TimeoutError):
                async with callbacks_queue.iterator(timeout=5) as messages_iterator:
                    async for message in messages_iterator:
                        async with message.process():
                            if self.__stop_event.is_set():
                                await message.nack()
                                break

                            if message.correlation_id != self.__correlation_id:
                                await message.nack()
                                continue

                            payload: dict[str, Any] = unpackb(message.body)
                            new_user_data = UpdateResponse(
                                user_id=payload["user_id"],
                                full_name=payload["full_name"],
                                username=payload["username"],
                            )
                            await self.__users_repository.update(new_user_data)

                            RECEIVED_BROKER_MESSAGES_TOTAL.labels(
                                consumer="users",
                                provider="bot",
                                title="received user data for updating",
                            ).inc()

    # def __get_scheduler(self) -> AsyncIOScheduler:
    #     return cast(AsyncIOScheduler, self.__scheduler)

    def __get_channel(self) -> AbstractChannel:
        if self.__channel is None:
            raise RuntimeError("The channel is None!")

        return self.__channel

    def __get_callbacks_queue(self) -> str:
        if self.__callbacks_queue_name is None:
            raise RuntimeError("The callback queue is None!")

        return self.__callbacks_queue_name

    def __clean(self) -> None:
        self.__channel = None
        self.__callbacks_queue_name = None
