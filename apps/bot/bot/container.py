from dependency_injector import containers, providers

from libs.settings.rabbit import RabbitSettings
from libs.settings.services import ServicesSettings
from libs.message_brokers.rabbit import RabbitConnector
from libs.logger import Logger
from .app import App
from .settings.bot import BotRunningType, BotSettings
from .settings.webhooks import WebhooksSettings
from .core.bot import Bot
from .core.bot_runners import BaseBotRunner, PollingBotRunner, WebhooksBotRunner
from .handlers.commands import CommandsRouter
from .handlers.commands.start import StartHandlerRouter
from .handlers.commands.logout import LogoutHandlerRouter
from .handlers.controllers.webhooks import WebhooksControllers
from .broker import UsersUpdaterRPCServer, NotificationsConsumer


class Container(containers.DeclarativeContainer):
    bot_settings = providers.Singleton(BotSettings)
    webhooks_settings = providers.Singleton(WebhooksSettings)
    rabbit_settings = providers.Singleton(RabbitSettings)
    services_settings = providers.Singleton(ServicesSettings)

    logger = providers.Singleton(Logger)
    rabbit_connector = providers.Singleton(RabbitConnector, rabbit_settings=rabbit_settings)

    # Telegram routes
    start_handler = providers.Singleton(
        StartHandlerRouter,
        services_settings=services_settings,
        logger=logger,
    )
    logout_handler = providers.Singleton(
        LogoutHandlerRouter,
        services_settings=services_settings,
        logger=logger,
    )
    commands_router = providers.Singleton(
        CommandsRouter, routers=providers.List(start_handler, logout_handler)
    )

    # Bot
    bot = providers.Singleton(
        Bot,
        bot_settings=bot_settings,
        routes=providers.List(commands_router),
    )
    bot_runner = providers.AbstractSingleton(BaseBotRunner)

    # Webhooks controllers
    webhooks_controller = providers.Singleton(
        WebhooksControllers,
        bot=bot,
        webhooks_settings=webhooks_settings,
        logger=logger,
    )

    # Broker
    users_updater = providers.Factory(
        UsersUpdaterRPCServer,
        bot=bot,
        connector=rabbit_connector,
        logger=logger,
    )
    notifications_consumer = providers.Factory(
        NotificationsConsumer,
        bot=bot,
        connector=rabbit_connector,
        logger=logger,
    )

    app = providers.Singleton(App, bot_runner=bot_runner, logger=logger)


class ContainerFactory:
    __container: Container

    def __init__(self) -> None:
        self.__container = self.__create_set_container()

    @classmethod
    def create(cls) -> Container:
        return cls().__container

    def __create_set_container(self) -> Container:
        container = Container()
        bot_running_type = container.bot_settings().type

        common_dependencies = {
            "bot": container.bot,
            "logger": container.logger,
            "users_updater": container.users_updater,
            "notifications_consumer": container.notifications_consumer,
        }

        match bot_running_type:
            case BotRunningType.POLLING:
                container.bot_runner.override(
                    providers.Singleton(PollingBotRunner, **common_dependencies)
                )

            case BotRunningType.WEBHOOKS:
                container.bot_runner.override(
                    providers.Singleton(
                        WebhooksBotRunner,
                        **common_dependencies,
                        webhooks_settings=container.webhooks_settings,
                        controllers=providers.List(container.webhooks_controller),
                    )
                )

        return container
