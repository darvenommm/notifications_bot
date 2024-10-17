from aio_pika import connect_robust
from aio_pika.pool import Pool, PoolItemContextManager
from aio_pika.abc import AbstractRobustConnection, AbstractChannel

from users.src.settings.main import main_settings


class RabbitConnector:
    __MAX_CONNECTIONS_COUNT = 2
    __MAX_CHANNELS_COUNT = 10

    __channels_pool: Pool[AbstractChannel] | None = None

    def get_connection(self) -> PoolItemContextManager[AbstractChannel]:
        if self.__channels_pool is None:
            raise TypeError("Channels pools has to be initialized!")

        return self.__channels_pool.acquire()

    async def init_pool(self) -> None:
        async def get_connection() -> AbstractRobustConnection:
            return await connect_robust(main_settings.queue_connection_string)

        connection_pool: Pool[AbstractRobustConnection] = Pool(
            get_connection,
            max_size=self.__MAX_CONNECTIONS_COUNT,
        )

        async def get_channel() -> AbstractChannel:
            async with connection_pool.acquire() as connection:
                return await connection.channel()

        self.__channels_pool = Pool(get_channel, max_size=self.__MAX_CHANNELS_COUNT)


queue_connector = RabbitConnector()
