from dependency_injector import containers, providers

from libs.databases.postgres import DBConnector
from libs.message_brokers.rabbit import RabbitConnector
from libs.settings.rabbit import RabbitSettings
from libs.settings.database import DatabaseSettings
from libs.logger import Logger
from .settings.users import UsersSettings
from .modules.users import UsersController, UsersUpdaterRPCClient, UsersRepository
from .app import App


class Container(containers.DeclarativeContainer):
    users_settings = providers.Singleton(UsersSettings)
    database_settings = providers.Singleton(DatabaseSettings)
    rabbit_settings = providers.Singleton(RabbitSettings)

    rabbit_connector = providers.Singleton(RabbitConnector, rabbit_settings=rabbit_settings)
    db_connector = providers.Singleton(DBConnector, database_settings=database_settings)
    logger = providers.Singleton(Logger)

    users_repository = providers.Singleton(UsersRepository, db_connector=db_connector)
    users_updater = providers.Factory(
        UsersUpdaterRPCClient,
        connector=rabbit_connector,
        users_repository=users_repository,
        logger=logger,
    )
    users_controller = providers.Singleton(UsersController, users_repository=users_repository)

    app = providers.Singleton(
        App,
        users_settings=users_settings,
        users_updater=users_updater,
        controllers=providers.List(users_controller),
    )
