from dependency_injector import containers, providers
from typing import Self

from .settings.envs.main import main_settings, BotType
from .app import App
from .core.bot import BaseBot, BotSettings
from .handlers.controllers.webhooks import WebhooksControllers


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    bot_settings = providers.Singleton(BotSettings)
    bot = providers.AbstractSingleton(BaseBot)

    webhooks_controller = providers.Singleton(WebhooksControllers, bot_settings=bot_settings)

    webhooks_bot_controllers = providers.List(webhooks_controller)

    app = providers.Singleton(App, bot=bot)


class ContainerFactory:
    __is_set = False

    __container: Container

    def __init__(self) -> None:
        self.__container = Container()
        self.__setup()

    @classmethod
    def create(cls) -> Container:
        current_factory = cls()

        return current_factory.__container

    def __setup(self) -> None:
        if not self.__is_set:
            self.__is_set = True
            self.__setup_bot()

    def __setup_bot(self) -> None:
        match main_settings.bot_type:
            case BotType.POLLING:
                from .core.bot.polling import PollingBot

                self.__container.bot.override(
                    providers.Singleton(
                        PollingBot,
                        bot_settings=self.__container.bot_settings,
                    )
                )

            case BotType.WEBHOOKS:
                from .core.bot.webhooks import WebhooksBot

                self.__container.bot.override(
                    providers.Singleton(
                        WebhooksBot,
                        bot_settings=self.__container.bot_settings,
                        controllers=self.__container.webhooks_bot_controllers,
                    )
                )


container = ContainerFactory.create()
