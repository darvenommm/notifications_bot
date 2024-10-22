from pydantic import BaseModel

from libs.contracts.users.dto import UpdateUserDTO


class UpdateRequest(BaseModel):
    user_id: int


class UpdateResponse(UpdateUserDTO):
    pass
