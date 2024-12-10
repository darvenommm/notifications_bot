from aiohttp import ClientSession
from aiogram.filters import CommandStart
from aiogram.types import Message
from http import HTTPStatus

from libs.settings.services import ServicesSettings
from libs.base_classes.bot_router import BotRouter
from libs.logger import Logger
from libs.contracts.users import AddUserDTO
from libs.metrics import calculate_execution_time, AIOGRAM_REQUEST_DURATION_SECONDS


class StartHandlerRouter(BotRouter):
    __services_settings: ServicesSettings
    __logger: Logger

    def __init__(self, services_settings: ServicesSettings, logger: Logger) -> None:
        super().__init__()

        self.__services_settings = services_settings
        self.__logger = logger

        self._router.message(CommandStart())(self.handle)

    @calculate_execution_time(
        AIOGRAM_REQUEST_DURATION_SECONDS.labels(server="bot", handler="start_handler")
    )
    async def handle(self, message: Message) -> None:
        self.__logger().info(f"Start handler running")
        user = message.from_user

        if user is None:
            self.__logger().info(f"Start handler user is None")
            return

        self.__logger().info(f"Start handler run by {user.full_name}")

        user_data = AddUserDTO(
            user_id=user.id,
            full_name=user.full_name,
            username=user.username,
        )
        path = f"{self.__services_settings.users_url}users"

        async with ClientSession() as session:
            async with session.post(path, json=user_data.model_dump()) as response:
                match response.status:
                    case HTTPStatus.CREATED:
                        self.__logger().info(f"Start handler: user was created")
                        await message.answer("Created")
                    case HTTPStatus.OK | HTTPStatus.NO_CONTENT:
                        self.__logger().info(f"Start handler: user already has been created")
                        await message.answer("You've been created already")
                    case _:
                        self.__logger().error(f"Start handler: Error with user creating")
                        await message.answer("Some error")
