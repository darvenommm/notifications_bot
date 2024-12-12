from dependency_injector import containers, providers

from libs.metrics import MetricsController
from libs.settings.services import ServicesSettings

from .app import App
from .controllers.auth import AuthController
from .controllers.notifications import NotificationsController
from .middlewares import AuthMiddleware
from .settings.proxy import ProxySettings


class Container(containers.Container):
    config = providers.Configuration()
    proxy_settings = providers.Singleton(ProxySettings)
    services_settings = providers.Singleton(ServicesSettings)

    auth_controller = providers.Singleton(AuthController, proxy_settings=proxy_settings)
    auth_middleware = providers.Singleton(AuthMiddleware, proxy_settings=proxy_settings)

    notifications_controller = providers.Singleton(
        NotificationsController,
        services_settings=services_settings,
        auth_middleware=auth_middleware,
    )

    metrics_controller = providers.Singleton(MetricsController)

    app = providers.Singleton(
        App,
        proxy_settings=proxy_settings,
        services_settings=services_settings,
        controllers=providers.List(metrics_controller, auth_controller, notifications_controller),
    )
