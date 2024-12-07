from typing import Iterable

from libs.base_classes.bot_router import BotRouter


class CommandsRouter(BotRouter):
    def __init__(self, routers: Iterable[BotRouter]) -> None:
        super().__init__()

        for router in routers:
            self._router.include_router(router.router)
