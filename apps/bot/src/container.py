from dependency_injector import containers, providers

from libs.message_brokers.rabbit import RabbitConnector
from libs.settings import RabbitSettings, ServicesSettings
from .app import App
from .core.bot import Bot
from .core.bot_runners import BaseBotRunner, PollingBotRunner, WebhooksBotRunner
from .settings import BotType, BotSettings, WebhooksSettings
from .handlers.controllers.webhooks import WebhooksControllers
from .handlers.commands import CommandsRouter
from .broker import UsersUpdaterRPCServer, NotificationsConsumer


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    bot_settings = providers.Singleton(BotSettings)
    webhooks_settings = providers.Singleton(WebhooksSettings)
    services_settings = providers.Singleton(ServicesSettings)
    rabbit_settings = providers.Singleton(RabbitSettings)

    rabbit_connector = providers.Singleton(
        RabbitConnector,
        connection_string=config.rabbit_connection_string,
    )

    commands_router = providers.Singleton(CommandsRouter)

    bot = providers.Singleton(
        Bot,
        bot_settings=bot_settings,
        routes=providers.List(commands_router),
    )
    bot_runner = providers.AbstractSingleton(BaseBotRunner)

    webhooks_controller = providers.Singleton(
        WebhooksControllers,
        bot=bot,
        webhooks_settings=webhooks_settings,
    )

    users_updater = providers.Factory(UsersUpdaterRPCServer, bot=bot, connector=rabbit_connector)
    notifications_consumer = providers.Factory(
        NotificationsConsumer,
        bot=bot,
        connector=rabbit_connector,
    )

    app = providers.Singleton(App, bot_runner=bot_runner)


class ContainerFactory:
    __is_set = False

    __container: Container

    def __init__(self) -> None:
        self.__container = Container()
        self.__setup()

    @classmethod
    def create(cls) -> Container:
        container = cls().__container
        container.config.rabbit_connection_string.from_value(
            container.rabbit_settings().rabbit_connection_string
        )

        return container

    def __setup(self) -> None:
        if not self.__is_set:
            self.__is_set = True
            self.__setup_bot()

    def __setup_bot(self) -> None:
        bot_type = self.__container.bot_settings().type

        match bot_type:
            case BotType.POLLING:
                self.__container.bot_runner.override(
                    providers.Singleton(
                        PollingBotRunner,
                        bot=self.__container.bot,
                        users_updater=self.__container.users_updater,
                        notifications_consumer=self.__container.notifications_consumer,
                    )
                )

            case BotType.WEBHOOKS:
                self.__container.bot_runner.override(
                    providers.Singleton(
                        WebhooksBotRunner,
                        bot=self.__container.bot,
                        users_updater=self.__container.users_updater,
                        notifications_consumer=self.__container.notifications_consumer,
                        webhooks_settings=self.__container.webhooks_settings,
                        controllers=providers.List(self.__container.webhooks_controller),
                    )
                )
