from sqlalchemy import select, insert, update, delete
from typing import Sequence

from libs.contracts.users import AddUserDTO, UpdateUserDTO
from users.src.db import DBConnector
from users.src.models import User


class UsersRepository:
    __db_connector: DBConnector

    def __init__(self, db_connector: DBConnector) -> None:
        self.__db_connector = db_connector

    async def get_one(self, user_id: int) -> User | None:
        async with self.__db_connector.get_connection() as session:
            execution_result = await session.execute(select(User).where(User.user_id == user_id))

            return execution_result.scalar_one_or_none()

    async def get_all(self) -> Sequence[User]:
        async with self.__db_connector.get_connection() as session:
            execution_result = await session.execute(select(User))

            return execution_result.scalars().all()

    async def add(self, user_data: AddUserDTO) -> None:
        async with self.__db_connector.get_connection() as session:
            add_statement = insert(User).values(
                user_id=user_data.user_id,
                full_name=user_data.full_name,
                username=user_data.username,
            )

            await session.execute(add_statement)
            await session.commit()

    async def remove(self, user_id: int) -> None:
        async with self.__db_connector.get_connection() as session:
            await session.execute(delete(User).where(User.user_id == user_id))
            await session.commit()

    async def update(self, user_data: UpdateUserDTO) -> None:
        async with self.__db_connector.get_connection() as session:
            update_statement = (
                update(User)
                .where(User.user_id == user_data.user_id)
                .values(full_name=user_data.full_name, username=user_data.username)
            )

            await session.execute(update_statement)
            await session.commit()
