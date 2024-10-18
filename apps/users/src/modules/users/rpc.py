import asyncio
from aio_pika import Message
from aio_pika.abc import AbstractChannel
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]
from uuid import uuid4
from msgpack import packb  # type: ignore[import-untyped]
from msgpack.fallback import unpackb  # type: ignore[import-untyped]
from pydantic import BaseModel
from typing import Any

from users.src.core.queue import queue_connector
from .repository import users_repository
from .dtos import UpdateUserDTO


class Payload(BaseModel):
    user_id: int


class UsersUpdaterRPCClient:
    __USERS_EXCHANGE = "USERS_EXCHANGE"
    __USERS_QUEUE = "USERS_QUEUE"

    __session: AbstractChannel | None = None
    __callbacks_queue_name: str | None = None
    __correlation_id: str = str(uuid4())

    async def start(self) -> asyncio.Task[None]:
        print("start users updater")
        async with queue_connector.get_connection() as session:
            self.__session = session

            await self.__declare()
            self.__set_scheduler()
            return asyncio.create_task(self.__start_listening_callbacks_queue())

    async def __declare(self) -> None:
        session = self.__get_session()

        users_exchange = await session.declare_exchange(self.__USERS_EXCHANGE, durable=True)
        users_queue = await session.declare_queue(self.__USERS_QUEUE, durable=True)
        await users_queue.bind(users_exchange, routing_key=self.__USERS_QUEUE)
        callbacks_queue = await session.declare_queue(exclusive=True)

        self.__callbacks_queue_name = callbacks_queue.name

    async def __job(self) -> None:
        print("start jobbing")
        users = await users_repository.get_all()
        session = self.__get_session()

        for user in users:
            print(f"processing user {user.user_id}")
            payload: bytes = packb(Payload(user_id=user.user_id).model_dump())
            message = Message(payload, reply_to=self.__get_callbacks_queue())

            users_exchange = await session.get_exchange(self.__USERS_EXCHANGE, ensure=True)
            await users_exchange.publish(message, self.__USERS_QUEUE)

    def __set_scheduler(self) -> None:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(self.__job, "cron", hour=0, minute=0)
        scheduler.start()

    async def __start_listening_callbacks_queue(self) -> None:
        session = self.__get_session()
        callbacks_queue = await session.get_queue(self.__get_callbacks_queue())

        async with callbacks_queue.iterator() as messages_iterator:
            async for message in messages_iterator:
                async with message.process():
                    try:
                        if message.correlation_id != self.__correlation_id:
                            await message.nack()
                            print("The message is not acked")
                            continue

                        payload: dict[str, Any] = unpackb(message.body)
                        new_user_data = UpdateUserDTO(
                            user_id=payload["user_id"],
                            full_name=payload["full_name"],
                            username=payload["username"],
                        )
                        await users_repository.update(new_user_data)

                        await message.ack()
                        print("The message is acked")
                    except Exception as exception:
                        await message.nack(requeue=False)
                        print(f"Failed to process message: {exception}")

    def __get_session(self) -> AbstractChannel:
        if self.__session is None:
            raise RuntimeError("The session is None!")

        return self.__session

    def __get_callbacks_queue(self) -> str:
        if self.__callbacks_queue_name is None:
            raise RuntimeError("The callback queue is None!")

        return self.__callbacks_queue_name

    def __clean(self) -> None:
        self.__session = None
        self.__callbacks_queue_name = None


users_updater_rpc_client = UsersUpdaterRPCClient()
