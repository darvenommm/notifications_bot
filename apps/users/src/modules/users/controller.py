from http import HTTPMethod, HTTPStatus
from fastapi import Response

from libs.base_classes.controller import Controller
from libs.contracts.users import UserSchema, AddUserDTO, GetAllUsersDTO
from .repository import UsersRepository


class UsersController(Controller):
    __users_repository: UsersRepository

    def __init__(self, users_repository: UsersRepository) -> None:
        super().__init__()
        self.__users_repository = users_repository
        self.__set_routes()

    def __set_routes(self) -> None:
        self._router.tags = ["users"]

        prefix = "/users"
        prefix_with_id = "/users/{user_id}"

        self._router.add_api_route(
            endpoint=self.get_all,
            path=prefix,
            methods=[HTTPMethod.GET],
            response_model=GetAllUsersDTO,
        )

        self._router.add_api_route(
            endpoint=self.add,
            path=prefix,
            methods=[HTTPMethod.POST],
        )

        self._router.add_api_route(
            endpoint=self.remove,
            path=prefix_with_id,
            methods=[HTTPMethod.DELETE],
            status_code=HTTPStatus.NO_CONTENT,
        )

    async def get_all(self) -> GetAllUsersDTO:
        users = await self.__users_repository.get_all()
        transformed_users = [
            UserSchema(
                user_id=user.user_id,
                full_name=user.full_name,
                username=user.username,
            )
            for user in users
        ]

        return GetAllUsersDTO(users=transformed_users)

    async def add(self, user_data: AddUserDTO) -> Response:
        status_code = HTTPStatus.NO_CONTENT
        user = await self.__users_repository.get_one(user_data.user_id)

        if not user:
            await self.__users_repository.add(user_data)
            status_code = HTTPStatus.CREATED

        return Response(None, status_code)

    async def remove(self, user_id: int) -> None:
        user = await self.__users_repository.get_one(user_id)

        if user:
            await self.__users_repository.remove(user_id)
