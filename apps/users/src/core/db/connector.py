from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from users.src.settings.main import main_settings


class DBConnector:
    __session_maker: async_sessionmaker[AsyncSession]

    def __init__(self) -> None:
        engine = create_async_engine(main_settings.db_connection_string, echo=True)
        self.__session_getter = async_sessionmaker(bind=engine)

    def get_connection(self) -> AsyncSession:
        return self.__session_maker()


db_connector = DBConnector()
