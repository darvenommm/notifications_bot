from aiogram import Router


class BotRouter:
    def __init__(self) -> None:
        super().__init__()
        self._router = Router()

    @property
    def router(self) -> Router:
        return self._router
