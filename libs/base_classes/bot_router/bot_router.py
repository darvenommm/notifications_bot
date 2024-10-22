import aiogram

if aiogram is None:
    pass

from abc import ABC
from aiogram import Router


class BotRouter(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._router = Router()

    @property
    def router(self) -> Router:
        return self._router
