from typing import Any

from fastapi import APIRouter


class Controller:
    _router: APIRouter

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._router = APIRouter()

    @property
    def router(self) -> APIRouter:
        return self._router
