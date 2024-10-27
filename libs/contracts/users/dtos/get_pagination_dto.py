from pydantic import BaseModel, PastDatetime

from ..user_schema import UserSchema


class GetPaginationDTO(BaseModel):
    users: list[UserSchema]
    cursor: PastDatetime | None
    pages_count: int
