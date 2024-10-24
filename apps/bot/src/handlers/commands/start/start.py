from aiohttp import ClientSession
from aiogram.handlers import MessageHandler
from aiogram.types import Message
from http import HTTPStatus

from libs.contracts.users import AddUserDTO
from libs.settings import ServicesSettings


class StartHandler(MessageHandler):
    __services_settings = ServicesSettings()

    async def handle(self) -> None:
        message: Message = self.event
        user = self.from_user

        if user is None:
            return

        user_data = AddUserDTO(user_id=user.id, full_name=user.full_name, username=user.username)
        path = f"{self.__services_settings.users_url}users"

        async with ClientSession() as session:
            async with session.post(path, json=user_data.model_dump()) as response:
                match response.status:
                    case HTTPStatus.CREATED:
                        await message.answer("Created")
                    case HTTPStatus.OK | HTTPStatus.NO_CONTENT:
                        await message.answer("You Created")
                    case _:
                        await message.answer("Some error")
