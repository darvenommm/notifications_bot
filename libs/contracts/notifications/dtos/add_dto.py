from pydantic import BaseModel
from typing import Literal


class AddNotificationDTO(BaseModel):
    reply_to: Literal["all"] | int
    message: str
