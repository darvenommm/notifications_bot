from dependency_injector import containers, providers

from libs.message_brokers.rabbit import RabbitConnector
from libs.metrics import MetricsController
from libs.settings.rabbit import RabbitSettings
from libs.settings.services import ServicesSettings

from .app import App
from .modules.notifications import NotificationsController, NotificationsPublisher
from .settings.notifications import NotificationsSettings


class Container(containers.DeclarativeContainer):
    notifications_settings = providers.Singleton(NotificationsSettings)
    services_settings = providers.Singleton(ServicesSettings)
    rabbit_settings = providers.Singleton(RabbitSettings)

    rabbit_connector = providers.Singleton(RabbitConnector, rabbit_settings=rabbit_settings)

    notification_publisher = providers.Singleton(
        NotificationsPublisher,
        connector=rabbit_connector,
        services_settings=services_settings,
    )

    notification_controller = providers.Singleton(
        NotificationsController,
        notification_publisher=notification_publisher,
    )
    metrics_controller = providers.Singleton(MetricsController)

    app = providers.Singleton(
        App,
        notifications_settings=notifications_settings,
        controllers=providers.List(metrics_controller, notification_controller),
    )
