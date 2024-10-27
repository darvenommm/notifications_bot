from aiohttp import ClientSession
from http import HTTPMethod, HTTPStatus
from fastapi.encoders import jsonable_encoder
from typing import Any

from libs.base_classes.controller import Controller
from libs.settings import ServicesSettings
from libs.contracts.notifications import AddNotificationDTO, SendRequest
from libs.contracts.users import GetAllUsersDTO
from .broker import NotificationsPublisher


class NotificationsController(Controller):
    __services_settings: ServicesSettings
    __notification_publisher: NotificationsPublisher

    def __init__(
        self,
        services_settings: ServicesSettings,
        notification_publisher: NotificationsPublisher,
    ) -> None:
        super().__init__()
        self.__services_settings = services_settings
        self.__notification_publisher = notification_publisher

        prefix = "/notifications"

        self._router.add_api_route(
            endpoint=self.add,
            path=prefix,
            methods=[HTTPMethod.POST],
            status_code=HTTPStatus.NO_CONTENT,
        )

    async def add(self, notification_data: AddNotificationDTO) -> None:
        if notification_data.reply_to != "all":
            send_data = SendRequest(
                reply_to=notification_data.reply_to,
                message=notification_data.message,
            )
            await self.__notification_publisher.send(send_data, notification_data.datetime)
        else:
            path = f"{self.__services_settings.users_url}users"

            async with ClientSession() as session:
                async with session.get(path) as response:
                    response_data: dict[str, Any] = await response.json()
                    users = GetAllUsersDTO(users=response_data["users"]).users

            for user in users:
                send_data = SendRequest(reply_to=user.user_id, message=notification_data.message)
                await self.__notification_publisher.send(send_data, notification_data.datetime)
