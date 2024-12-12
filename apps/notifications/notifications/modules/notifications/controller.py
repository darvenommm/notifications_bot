from datetime import datetime
from http import HTTPMethod, HTTPStatus
from typing import Any

from aiohttp import ClientSession

from libs.base_classes.controller import Controller
from libs.contracts.notifications import AddNotificationDTO, SendRequest
from libs.contracts.users import GetPaginationDTO
from libs.settings.services import ServicesSettings

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
        path = f"{self.__services_settings.users_url}users"

        async with ClientSession() as session:
            cursor: datetime | None = datetime.min
            while cursor is not None:
                params: dict[str, Any] = {"cursor": cursor.isoformat(), "limit": 20}

                async with session.get(path, params=params) as response:
                    response_data: dict[str, Any] = await response.json()
                    pagination_info = GetPaginationDTO(
                        users=response_data["users"],
                        cursor=response_data["cursor"],
                        pages_count=response_data["pages_count"],
                    )
                    cursor = pagination_info.cursor

                for user in pagination_info.users:
                    await self.__notification_publisher.send(
                        SendRequest(reply_to=user.user_id, message=notification_data.message),
                        notification_data.datetime,
                    )
