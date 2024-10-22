import fastapi


if fastapi is None:
    raise RuntimeError("Not found fastapi package")


from fastapi import APIRouter


class Controller:
    _router: APIRouter

    def __init__(self) -> None:
        self._router = APIRouter()

    @property
    def router(self) -> APIRouter:
        return self._router
