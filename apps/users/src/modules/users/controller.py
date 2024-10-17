from http import HTTPMethod, HTTPStatus
from fastapi import Response

from users.src.core.controller import Controller
from .dtos import AddUserDTO, UpdateUserDTO, GetAllUsersResponse
from .schema import UserResponseSchema
from .repository import users_repository


class UsersController(Controller):
    def __init__(self) -> None:
        super().__init__()
        self._router.tags = ["users"]

        prefix = "/users"
        prefix_with_id = "/users/{user_id}"

        self._router.add_api_route(
            endpoint=self.get_all,
            path=prefix,
            methods=[HTTPMethod.GET],
            response_model=GetAllUsersResponse,
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

    async def get_all(self) -> GetAllUsersResponse:
        users = await users_repository.get_all()
        transformed_users = [
            UserResponseSchema(
                user_id=user.user_id,
                full_name=user.full_name,
                username=user.username,
            )
            for user in users
        ]

        return GetAllUsersResponse(users=transformed_users)

    async def add(self, user_data: AddUserDTO) -> Response:
        status_code = HTTPStatus.NO_CONTENT
        user = await users_repository.get_one(user_data.user_id)

        if not user:
            await users_repository.add(user_data)
            status_code = HTTPStatus.CREATED

        return Response(None, status_code)

    async def remove(self, user_id: int) -> None:
        user = await users_repository.get_one(user_id)

        if user:
            await users_repository.remove(user_id)


users_controller = UsersController()
