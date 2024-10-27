from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from users.src.settings import MainSettings


class DBConnector:
    __session_maker: async_sessionmaker[AsyncSession]

    def __init__(self, main_settings: MainSettings) -> None:
        engine = create_async_engine(main_settings.db_connection_string, echo=True)
        self.__session_maker = async_sessionmaker(bind=engine)

    def get_session(self) -> AsyncSession:
        return self.__session_maker()
