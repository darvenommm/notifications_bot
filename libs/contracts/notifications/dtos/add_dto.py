from pydantic import BaseModel, FutureDatetime


class AddNotificationDTO(BaseModel):
    message: str
    datetime: FutureDatetime
