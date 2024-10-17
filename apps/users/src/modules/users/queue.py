from aio_pika import Message
from aio_pika.abc import AbstractChannel
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]
from msgpack import packb  # type: ignore[import-untyped]
from msgpack.fallback import unpackb  # type: ignore[import-untyped]
from pydantic import BaseModel
from typing import Any, cast

from users.src.core.queue import queue_connector
from .repository import users_repository
from .dtos import UpdateUserDTO


class DeclareInfo(BaseModel):
    reply_to: str


class Request(BaseModel):
    user_id: int


class UsersUpdater:
    USERS_EXCHANGE = "USERS_EXCHANGE"
    USERS_QUEUE = "USERS_QUEUE"

    async def __declare(self, session: AbstractChannel) -> DeclareInfo:
        exchange = await session.declare_exchange(self.USERS_EXCHANGE, durable=True)
        queue = await session.declare_queue(self.USERS_QUEUE, durable=True)
        await queue.bind(exchange, routing_key=self.USERS_QUEUE)

        response_queue = await session.declare_queue(exclusive=True)

        return DeclareInfo(reply_to=response_queue.name)

    async def __background_job(self, session: AbstractChannel, reply_to: str) -> None:
        users = await users_repository.get_all()

        for user in users:
            payload: bytes = packb(Request(user_id=user.user_id).model_dump())
            message = Message(payload, headers={"reply-to": reply_to})

            users_exchange = await session.get_exchange(self.USERS_EXCHANGE, ensure=True)
            await users_exchange.publish(message, self.USERS_QUEUE)

    async def __listen_response_queue(self, session: AbstractChannel, reply_to: str) -> None:
        response_queue = await session.get_queue(reply_to)

        async with response_queue.iterator() as messages_iterator:
            async for message in messages_iterator:
                async with message.process():
                    user_id = cast(int | None, message.headers.get("correlation-id"))
                    print(user_id, type(user_id))

                    if not user_id:
                        return await message.ack()

                    payload: dict[str, Any] = unpackb(message.body)
                    user_data = UpdateUserDTO(
                        full_name=payload["full_name"],
                        username=payload["username"],
                    )
                    await users_repository.update(user_id, user_data)

                    await message.ack()

    async def run(self) -> None:
        async with queue_connector.get_connection() as session:
            declare_info = await self.__declare(session)
            reply_to = declare_info.reply_to

            job = lambda: self.__background_job(session, reply_to)
            scheduler = AsyncIOScheduler()
            scheduler.add_job(job, "cron", hour=0, minute=0)
            scheduler.start()

            await self.__listen_response_queue(session, reply_to)


users_updater = UsersUpdater()
