from pydantic import BaseModel, Field


class UserResponseSchema(BaseModel):
    user_id: int
    full_name: str
    username: str | None = Field(...)
