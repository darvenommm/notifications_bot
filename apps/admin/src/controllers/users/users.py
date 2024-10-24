from aiohttp import ClientSession
from http import HTTPMethod
from fastapi import Depends

from libs.base_classes.controller import Controller
from libs.settings import ServicesSettings
from libs.contracts.users import GetAllUsersDTO
from admin.src.middlewares import AuthMiddleware


class UsersController(Controller):
    __services_settings: ServicesSettings

    def __init__(
        self,
        services_settings: ServicesSettings,
        auth_middleware: AuthMiddleware,
    ) -> None:
        super().__init__()
        self.__services_settings = services_settings

        self._router.add_api_route(
            endpoint=self.get_users,
            path="/users",
            methods=[HTTPMethod.GET],
            dependencies=[Depends(auth_middleware.middleware)],
        )

    async def get_users(self) -> GetAllUsersDTO:
        path = f"{self.__services_settings.users_url}users"

        async with ClientSession() as session:
            async with session.get(path) as response:
                return await response.json()
