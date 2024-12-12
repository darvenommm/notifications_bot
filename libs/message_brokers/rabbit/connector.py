from typing import TypeAlias

from aio_pika import connect_robust
from aio_pika.abc import AbstractChannel, AbstractRobustConnection
from aio_pika.pool import Pool, PoolItemContextManager

from libs.settings.rabbit import RabbitSettings


class RabbitConnector:
    __DEFAULT_MAX_CONNECTIONS = 2
    __DEFAULT_MAX_CHANNELS = 10

    __max_connections: int
    __max_channels: int

    __rabbit_settings: RabbitSettings
    __channels_pool: Pool[AbstractChannel] | None = None

    def __init__(
        self,
        rabbit_settings: RabbitSettings,
        *,
        max_connections: int = __DEFAULT_MAX_CONNECTIONS,
        max_channels: int = __DEFAULT_MAX_CHANNELS,
    ) -> None:
        self.__rabbit_settings = rabbit_settings
        self.max_connections = max_connections
        self.max_channels = max_channels
        self.__set_up()

    def get_channel(self) -> PoolItemContextManager[AbstractChannel]:
        if self.__channels_pool is None:
            raise RuntimeError("You didn't inited the RabbitConnector")

        return self.__channels_pool.acquire()

    def __set_up(self) -> None:
        async def get_connection() -> AbstractRobustConnection:
            return await connect_robust(self.__rabbit_settings.rabbit_connection_string)

        ConnectionsPoolType: TypeAlias = Pool[AbstractRobustConnection]
        connection_pool: ConnectionsPoolType = Pool(get_connection, max_size=self.max_connections)

        async def get_channel() -> AbstractChannel:
            async with connection_pool.acquire() as connection:
                return await connection.channel()

        self.__channels_pool = Pool(get_channel, max_size=self.max_channels)

    @property
    def max_connections(self) -> int:
        return self.__max_connections

    @max_connections.setter
    def max_connections(self, new_max_connections: int) -> None:
        if not (new_max_connections > 0):
            raise ValueError("Incorrect max connections count, Should be greater than 0!")

        self.__max_connections = new_max_connections

    @property
    def max_channels(self) -> int:
        return self.__max_channels

    @max_channels.setter
    def max_channels(self, new_max_channels: int) -> None:
        if not (new_max_channels > 0):
            raise ValueError("Incorrect max connections count, Should be greater than 0!")

        self.__max_channels = new_max_channels

    def reset(self) -> None:
        self.max_connections = self.__DEFAULT_MAX_CONNECTIONS
        self.max_channels = self.__DEFAULT_MAX_CHANNELS
