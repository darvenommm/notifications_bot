from pydantic import BaseModel

from libs.contracts.users.dtos import UpdateUserDTO


class UpdateRequest(BaseModel):
    user_id: int


class UpdateResponse(UpdateUserDTO):
    pass
