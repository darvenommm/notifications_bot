from pydantic import BaseModel

from ..schema import UserResponseSchema


class GetAllUsersResponse(BaseModel):
    users: list[UserResponseSchema]
