from pydantic import BaseModel


class SendRequest(BaseModel):
    reply_to: int
    message: str
