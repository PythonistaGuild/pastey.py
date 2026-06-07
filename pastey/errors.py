from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientResponse
    from requests import Response

__all__ = ("APIError", "ForbiddenError", "NotFoundError", "UnauthorizedError", "error_factory")


class APIError(Exception):
    __slots__ = ("message", "paste_id", "response", "status_code")

    def __init__(
        self,
        *,
        status_code: int,
        paste_id: str | None = None,
        message: str | None = None,
        response: ClientResponse | Response,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.response = response
        self.status_code = status_code
        self.paste_id = paste_id


class NotFoundError(APIError):
    def __init__(self, *, paste_id: str, response: ClientResponse | Response) -> None:
        super().__init__(
            status_code=404, paste_id=paste_id, message=f"Paste with id {paste_id} not found.", response=response
        )


class ForbiddenError(APIError):
    def __init__(self, *, response: ClientResponse | Response) -> None:
        super().__init__(status_code=403, message="You are forbidden from performing this action", response=response)


class UnauthorizedError(APIError):
    def __init__(self, *, paste_id: str, response: ClientResponse | Response) -> None:
        super().__init__(
            status_code=401,
            paste_id=paste_id,
            message=f"You must provide the password to view paste {paste_id!r}.",
            response=response,
        )


def error_factory(code: int, /) -> type[APIError]:
    if code == 401:
        return UnauthorizedError
    if code == 403:
        return ForbiddenError
    if code == 404:
        return NotFoundError
    return APIError
