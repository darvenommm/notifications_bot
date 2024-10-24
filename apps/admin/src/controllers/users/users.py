from aiohttp import ClientSession

from libs.base_classes.controller import Controller


class UsersController(Controller):
    def __init__(self) -> None:
        super().__init__()
