from http import HTTPMethod, HTTPStatus
from fastapi import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from libs.base_classes.controller import Controller


class MetricsController(Controller):
    def __init__(self) -> None:
        super().__init__()
        self._router.add_api_route(
            endpoint=self.metrics,
            path="/metrics",
            methods=[HTTPMethod.GET],
            status_code=HTTPStatus.OK,
        )

    async def metrics(self) -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
