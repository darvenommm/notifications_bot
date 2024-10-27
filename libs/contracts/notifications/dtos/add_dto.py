from pydantic import BaseModel, FutureDatetime
from typing import Literal


class AddNotificationDTO(BaseModel):
    reply_to: Literal["all"] | int
    message: str
    datetime: FutureDatetime
