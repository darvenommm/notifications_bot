from http import HTTPMethod, HTTPStatus

from libs.base_classes.controller import Controller
from libs.contracts.notifications import AddNotificationDTO

from .publisher import NotificationsPublisher


class NotificationsController(Controller):
    __notification_publisher: NotificationsPublisher

    def __init__(
        self,
        notification_publisher: NotificationsPublisher,
    ) -> None:
        super().__init__()
        self.__notification_publisher = notification_publisher

        prefix = "/notifications"

        self._router.add_api_route(
            endpoint=self.add,
            path=prefix,
            methods=[HTTPMethod.POST],
            status_code=HTTPStatus.NO_CONTENT,
        )

    async def add(self, notification_data: AddNotificationDTO) -> None:
        self.__notification_publisher.schedule_notification(notification_data)
