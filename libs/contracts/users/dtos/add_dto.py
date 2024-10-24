from pydantic import BaseModel, Field


class AddUserDTO(BaseModel):
    user_id: int
    full_name: str
    username: str | None = Field(...)
