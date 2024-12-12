from dependency_injector import containers, providers

from libs.databases.postgres import DBConnector
from libs.logger import Logger
from libs.message_brokers.rabbit import RabbitConnector
from libs.metrics import MetricsController
from libs.settings.database import DatabaseSettings
from libs.settings.rabbit import RabbitSettings

from .app import App
from .modules.users import UsersController, UsersRepository, UsersUpdaterRPCClient
from .settings.users import UsersSettings


class Container(containers.DeclarativeContainer):
    users_settings = providers.Singleton(UsersSettings)
    database_settings = providers.Singleton(DatabaseSettings)
    rabbit_settings = providers.Singleton(RabbitSettings)

    rabbit_connector = providers.Singleton(RabbitConnector, rabbit_settings=rabbit_settings)
    db_connector = providers.Singleton(DBConnector, database_settings=database_settings)
    logger = providers.Singleton(Logger)

    metrics_controller = providers.Singleton(MetricsController)

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
        controllers=providers.List(metrics_controller, users_controller),
    )
