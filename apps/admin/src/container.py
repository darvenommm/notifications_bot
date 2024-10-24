from dependency_injector import containers, providers

from libs.settings import ServicesSettings
from .settings import MainSettings
from .middlewares import AuthMiddleware
from .controllers.auth import AuthController
from .controllers.users import UsersController
from .controllers.notifications import NotificationsController
from .app import App


class Container(containers.Container):
    config = providers.Configuration()
    main_settings = providers.Singleton(MainSettings)
    services_settings = providers.Singleton(ServicesSettings)

    auth_controller = providers.Singleton(AuthController, main_settings=main_settings)
    auth_middleware = providers.Singleton(AuthMiddleware, main_settings=main_settings)

    users_controller = providers.Singleton(
        UsersController,
        services_settings=services_settings,
        auth_middleware=auth_middleware,
    )

    notifications_controller = providers.Singleton(
        NotificationsController,
        services_settings=services_settings,
        auth_middleware=auth_middleware,
    )

    app = providers.Singleton(
        App,
        main_settings=main_settings,
        controllers=providers.List(auth_controller, users_controller, notifications_controller),
    )
