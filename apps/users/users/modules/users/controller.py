import asyncio
from datetime import datetime
from http import HTTPMethod, HTTPStatus
from math import ceil
from typing import Annotated

from fastapi import Query, Response

from libs.base_classes.controller import Controller
from libs.contracts.users import AddUserDTO, GetPaginationDTO, UserSchema

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
            endpoint=self.get_page,
            path=prefix,
            methods=[HTTPMethod.GET],
            response_model=GetPaginationDTO,
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

    async def get_page(
        self,
        cursor: Annotated[datetime, Query()] = datetime.min,
        limit: Annotated[int, Query(ge=1)] = 10,
    ) -> GetPaginationDTO:
        (users, users_count) = await asyncio.gather(
            self.__users_repository.get_page(cursor, limit), self.__users_repository.get_count()
        )
        last_user = None if len(users) == 0 else users[-1]
        schemed_users = [
            UserSchema(
                user_id=user.user_id,
                full_name=user.full_name,
                username=user.username,
            )
            for user in users
        ]

        return GetPaginationDTO(
            users=schemed_users,
            cursor=last_user.created_at if last_user else None,
            pages_count=ceil(users_count / limit),
        )

    async def add(self, user_data: AddUserDTO) -> Response:
        status_code = HTTPStatus.NO_CONTENT
        user = await self.__users_repository.get_one(user_data.user_id)

        if not user:
            await self.__users_repository.add(user_data)
            status_code = HTTPStatus.CREATED

        return Response(None, status_code)

    async def remove(self, user_id: int) -> Response:
        status_code = HTTPStatus.OK
        user = await self.__users_repository.get_one(user_id)

        if user:
            await self.__users_repository.remove(user_id)
            status_code = HTTPStatus.NO_CONTENT

        return Response(None, status_code)
