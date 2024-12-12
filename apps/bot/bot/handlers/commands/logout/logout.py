from http import HTTPStatus

from aiogram.filters import Command
from aiogram.types import Message
from aiohttp import ClientSession

from libs.base_classes.bot_router import BotRouter
from libs.logger import Logger
from libs.metrics import AIOGRAM_REQUEST_DURATION_SECONDS, calculate_execution_time
from libs.settings.services import ServicesSettings


class LogoutHandlerRouter(BotRouter):
    __services_settings: ServicesSettings
    __logger: Logger

    def __init__(self, services_settings: ServicesSettings, logger: Logger) -> None:
        super().__init__()

        self.__services_settings = services_settings
        self.__logger = logger

        self._router.message(Command("logout"))(self.handle)

    @calculate_execution_time(
        AIOGRAM_REQUEST_DURATION_SECONDS.labels(server="bot", handler="logout_handler")
    )
    async def handle(self, message: Message) -> None:
        user = message.from_user

        if user is None:
            self.__logger().info("Logout handler user is None")
            return

        self.__logger().info(f"Logout handler run by {user.full_name}")
        path = f"{self.__services_settings.users_url}users/{user.id}"

        async with ClientSession() as session:
            async with session.delete(path) as response:
                self.__logger().info(f"Logout handler: response status {response.status}")

                match response.status:
                    case HTTPStatus.NO_CONTENT:
                        self.__logger().info("Logout handler: user unsubscribed")
                        await message.answer("You're unsubscribed")
                    case HTTPStatus.OK:
                        self.__logger().info("Logout handler: user wasn't subscribed")
                        await message.answer("You wasn't subscribed")
                    case _:
                        self.__logger().error("Logout handler: Error with user creating")
                        await message.answer("Some error")
