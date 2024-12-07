from aiohttp import ClientSession
from http import HTTPMethod
from fastapi import Response, Depends
from fastapi.encoders import jsonable_encoder

from libs.base_classes.controller import Controller
from libs.contracts.notifications import AddNotificationDTO
from libs.settings.services import ServicesSettings
from proxy.middlewares import AuthMiddleware


class NotificationsController(Controller):
    __services_settings: ServicesSettings

    def __init__(
        self,
        services_settings: ServicesSettings,
        auth_middleware: AuthMiddleware,
    ) -> None:
        super().__init__()
        self.__services_settings = services_settings

        self._router.add_api_route(
            endpoint=self.add,
            path="/notifications",
            methods=[HTTPMethod.POST],
            dependencies=[Depends(auth_middleware.middleware)],
        )

    async def add(self, notification_data: AddNotificationDTO) -> Response:
        path = f"{self.__services_settings.notifications_url}notifications"

        async with ClientSession() as session:
            async with session.post(path, json=jsonable_encoder(notification_data)) as response:
                return Response(status_code=response.status)
