from dependency_injector import containers, providers

from libs.message_brokers.rabbit import RabbitConnector
from libs.settings import RabbitSettings
from .settings import MainSettings
from .db import DBConnector
from .modules.users import UsersController, UsersUpdaterRPCClient, UsersRepository
from .app import App


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    main_settings = providers.Singleton(MainSettings)
    rabbit_settings = providers.Singleton(RabbitSettings)

    rabbit_connector = providers.Singleton(
        RabbitConnector,
        connection_string=config.rabbit_connection_string,
    )

    db_connector = providers.Singleton(DBConnector, main_settings=main_settings)

    users_repository = providers.Singleton(UsersRepository, db_connector=db_connector)
    users_updater = providers.Factory(
        UsersUpdaterRPCClient,
        connector=rabbit_connector,
        users_repository=users_repository,
    )
    users_controller = providers.Singleton(UsersController, users_repository=users_repository)

    app = providers.Singleton(
        App,
        main_settings=main_settings,
        users_updater=users_updater,
        controllers=providers.List(users_controller),
    )
