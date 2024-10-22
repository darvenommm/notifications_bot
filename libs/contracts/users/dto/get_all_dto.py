from pydantic import BaseModel

from ..user_schema import UserSchema


class GetAllUsersDTO(BaseModel):
    users: list[UserSchema]
