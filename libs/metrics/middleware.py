from http import HTTPStatus
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Awaitable, Callable, Type, Self

from .metrics import HTTP_REQUEST_TOTAL, HTTP_REQUEST_SUCCESS_TOTAL


class RequestMetricsMiddleware(BaseHTTPMiddleware):
    __server_name: str | None = None

    @classmethod
    def set_server(cls, server_name: str) -> Type[Self]:
        cls.__server_name = server_name

        return cls

    @property
    def server_name(self) -> str:
        if self.__server_name is None:
            raise RuntimeError("Not set server_name in PrometheusMiddleware")

        return self.__server_name

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        method = request.method
        path = request.url.path

        HTTP_REQUEST_TOTAL.labels(server=self.server_name, method=method, path=path).inc()

        response: Response = await call_next(request)

        status = response.status_code
        is_2xx = HTTPStatus(status).is_success
        is_3xx = HTTPStatus(status).is_redirection

        if is_2xx or is_3xx:
            HTTP_REQUEST_SUCCESS_TOTAL.labels(
                server=self.server_name,
                method=method,
                path=path,
                status=status,
            ).inc()

        return response
