import asyncio
from aio_pika import Message
from aio_pika.abc import AbstractChannel
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]
from uuid import uuid4
from msgpack import packb  # type: ignore[import-untyped]
from msgpack.fallback import unpackb  # type: ignore[import-untyped]
from typing import Any, cast

from libs.message_brokers.rabbit import RabbitConnector
from libs.contracts.users import USERS_EXCHANGE, USERS_QUEUE, UpdateRequest, UpdateResponse
from .repository import UsersRepository


class UsersUpdaterRPCClient:
    __channel: AbstractChannel | None = None
    __callbacks_queue_name: str | None = None
    __scheduler: AsyncIOScheduler
    __stop_event: asyncio.Event
    __correlation_id: str = str(uuid4())

    __connector: RabbitConnector
    __users_repository: UsersRepository

    def __init__(self, connector: RabbitConnector, users_repository: UsersRepository) -> None:
        self.__connector = connector
        self.__users_repository = users_repository
        self.__scheduler = AsyncIOScheduler()
        self.__stop_event = asyncio.Event()

    async def start(self) -> asyncio.Task[None]:
        print("start users updater")
        async with self.__connector.get_channel() as channel:
            self.__channel = channel

            await self.__declare()
            self.__set_scheduler()
            return asyncio.create_task(self.__start_listening_callbacks_queue())

    def stop(self) -> None:
        print("Stop UsersUpdaterRPCClient")
        self.__stop_event.set()
        self.__get_scheduler().shutdown()
        self.__clean()

    async def __declare(self) -> None:
        session = self.__get_channel()

        users_exchange = await session.declare_exchange(USERS_EXCHANGE, durable=True)
        users_queue = await session.declare_queue(USERS_QUEUE, durable=True)
        await users_queue.bind(users_exchange, routing_key=USERS_QUEUE)

        callbacks_queue = await session.declare_queue(exclusive=True)
        self.__callbacks_queue_name = callbacks_queue.name

    async def __job(self) -> None:
        print("start jobbing")
        users = await self.__users_repository.get_all()
        session = self.__get_channel()

        for user in users:
            payload: bytes = packb(UpdateRequest(user_id=user.user_id).model_dump())
            message = Message(
                payload,
                message_id=str(uuid4()),
                reply_to=self.__get_callbacks_queue(),
                correlation_id=self.__correlation_id,
            )

            users_exchange = await session.get_exchange(USERS_EXCHANGE, ensure=True)
            await users_exchange.publish(message, USERS_QUEUE)

    def __set_scheduler(self) -> None:
        print("set schedular")
        scheduler = self.__get_scheduler()
        scheduler.add_job(self.__job, "interval", seconds=20)
        scheduler.start()

    async def __start_listening_callbacks_queue(self) -> None:
        print("start listening")
        session = self.__get_channel()
        callbacks_queue = await session.get_queue(self.__get_callbacks_queue())

        while not self.__stop_event.is_set():
            try:
                async with callbacks_queue.iterator(timeout=1) as messages_iterator:
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
            except TimeoutError:
                pass

    def __get_scheduler(self) -> AsyncIOScheduler:
        return cast(AsyncIOScheduler, self.__scheduler)

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
