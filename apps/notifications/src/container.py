from dependency_injector import containers, providers

from libs.message_brokers.rabbit import RabbitConnector
from libs.settings import RabbitSettings, ServicesSettings
from .settings import MainSettings
from .modules.notifications import NotificationsController, NotificationsPublisher
from .app import App


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    main_settings = providers.Singleton(MainSettings)
    rabbit_settings = providers.Singleton(RabbitSettings)
    services_settings = providers.Singleton(ServicesSettings)

    rabbit_connector = providers.Singleton(
        RabbitConnector,
        connection_string=config.rabbit_connection_string,
    )

    notification_publisher = providers.Singleton(NotificationsPublisher, connector=rabbit_connector)

    notification_controller = providers.Singleton(
        NotificationsController,
        services_settings=services_settings,
        notification_publisher=notification_publisher,
    )

    app = providers.Singleton(
        App,
        main_settings=main_settings,
        controllers=providers.List(notification_controller),
    )
