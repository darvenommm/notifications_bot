from aiohttp import ClientSession
from datetime import datetime
from http import HTTPMethod, HTTPStatus
from typing import Any

from libs.base_classes.controller import Controller
from libs.settings import ServicesSettings
from libs.contracts.notifications import AddNotificationDTO, SendRequest
from libs.contracts.users import GetPaginationDTO
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
            await self.__add_all(notification_data)

    async def __add_all(self, notification_data: AddNotificationDTO) -> None:
        if notification_data.reply_to != "all":
            raise RuntimeError("Incorrect place for calling __add_all method!")

        path = f"{self.__services_settings.users_url}users"

        async with ClientSession() as session:
            cursor: datetime | None = datetime.min
            limit = 1

            while cursor is not None:
                params: dict[str, Any] = {"cursor": cursor.isoformat(), "limit": limit}
                print(params)

                async with session.get(path, params=params) as response:
                    response_data: dict[str, Any] = await response.json()
                    print(response_data)
                    pagination_info = GetPaginationDTO(
                        users=response_data["users"],
                        cursor=response_data["cursor"],
                        pages_count=response_data["pages_count"],
                    )
                    cursor = pagination_info.cursor

                for user in pagination_info.users:
                    print("user", user)
                    await self.__notification_publisher.send(
                        SendRequest(reply_to=user.user_id, message=notification_data.message),
                        notification_data.datetime,
                    )
