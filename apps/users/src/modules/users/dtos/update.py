from pydantic import BaseModel, Field


class UpdateUserDTO(BaseModel):
    full_name: str
    username: str | None = Field(...)
