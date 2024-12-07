from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from libs.settings.database import DatabaseSettings


class DBConnector:
    __session_maker: async_sessionmaker[AsyncSession]

    def __init__(self, database_settings: DatabaseSettings) -> None:
        engine = create_async_engine(database_settings.db_connection_string, echo=True)
        self.__session_maker = async_sessionmaker(bind=engine)

    def get_session(self) -> AsyncSession:
        return self.__session_maker()
