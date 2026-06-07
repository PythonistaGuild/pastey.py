from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

import aiohttp

from .errors import error_factory
from .paste import Paste
from .utils import base_url, create_payload

if TYPE_CHECKING:
    import datetime
    from types import TracebackType
    from typing import TypeVar

    from types_.paste import PasteyCreateResponse, PasteyGetResponse
    from typing_extensions import Self

    from .file import File

    BE = TypeVar("BE", bound=BaseException)

try:
    import requests
except ModuleNotFoundError:
    has_requests_ = False
else:
    has_requests_ = True
HAS_REQUESTS = has_requests_

__all__ = ("Client", "SyncClient")


class Client:
    __base_url__ = base_url()
    __slots__ = ("__owns_session__", "session")

    def __init__(self, *, session: aiohttp.ClientSession | None = None, base_url: str | None = None) -> None:
        if session:
            self.__owns_session__ = False
            self.session = session
        else:
            self.__owns_session__ = True
            self.session = aiohttp.ClientSession()
        if base_url:
            self.__class__.__base_url__ = base_url

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, type_: type[BE] | None, value: BE, traceback: TracebackType) -> None:  # noqa: PYI036 # not expanding the typevar
        await self.close()

    @overload
    async def get_paste(self, paste_id: str, *, password: str | None = None, raw: Literal[True]) -> str: ...

    @overload
    async def get_paste(self, paste_id: str, *, password: str | None = None, raw: Literal[False]) -> Paste: ...

    @overload
    async def get_paste(self, paste_id: str, *, password: str | None = None, raw: bool = ...) -> Paste: ...

    async def get_paste(self, paste_id: str, *, password: str | None = None, raw: bool = False) -> Paste | str:
        headers = None
        if password:
            headers = {"Authorization": password}

        async with self.session.get(f"{self.__base_url__}/pastes/{paste_id}", headers=headers) as resp:
            if 200 < resp.status <= 299:
                err = error_factory(resp.status)
                raise err(status_code=resp.status, paste_id=paste_id, response=resp)

            data: PasteyGetResponse = await resp.json()

        if raw:
            return data["files"][0]["content"]
        return Paste.from_payload(self, data)

    async def create_paste(
        self,
        *,
        files: list[File],
        expires_at: datetime.datetime | None = None,
        password: str | None = None,
        remaining_views: int | None = None,
    ) -> Paste:
        payload = create_payload(files=files, expires_at=expires_at, password=password, remaining_views=remaining_views)

        async with self.session.post(f"{self.__base_url__}/pastes", json=payload) as resp:
            if 200 < resp.status <= 299:
                err = error_factory(resp.status)
                raise err(status_code=resp.status, response=resp)

            data: PasteyCreateResponse = await resp.json()

        return Paste.from_payload(self, data)

    async def delete_paste(self, paste_id: str, safety_token: str) -> None:
        async with self.session.delete(
            f"{self.__base_url__}/pastes/{paste_id}", headers={"X-Safety-Token": safety_token}
        ) as resp:
            if 200 < resp.status <= 299:
                err = error_factory(resp.status)
                raise err(status_code=resp.status, paste_id=paste_id, response=resp)

    async def close(self) -> None:
        if self.__owns_session__:
            await self.session.close()


class SyncClient:
    __base_url__ = base_url()
    __slots__ = ("__owns_session__", "session")

    def __init__(self, *, session: requests.Session | None = None, base_url: str | None = None) -> None:
        if not HAS_REQUESTS:
            raise RuntimeError("Please install the library using the [sync] extra.")
        if session:
            self.__owns_session__ = False
            self.session = session
        else:
            self.__owns_session__ = True
            self.session = requests.Session()  # pyright: ignore[reportPossiblyUnboundVariable] # guarded
        if base_url:
            self.__class__.__base_url__ = base_url

    def __enter__(self) -> Self:
        return self

    def __exit__(self, type_: type[BE] | None, value: BE, traceback: TracebackType) -> None:  # noqa: PYI036 # not expanding the typevar
        self.close()

    @overload
    def get_paste(self, paste_id: str, *, password: str | None = None, raw: Literal[True]) -> str: ...

    @overload
    def get_paste(self, paste_id: str, *, password: str | None = None, raw: Literal[False]) -> Paste: ...

    def get_paste(
        self,
        paste_id: str,
        *,
        password: str | None = None,
        raw: bool = False,
        skip_view_increment: bool = False,
        safety_token: str | None = None,
    ) -> Paste | str:
        url = f"{self.__base_url__}/pastes/{paste_id}"
        headers: dict[str, str] = {}
        if password:
            headers["Authorization"] = password
        if safety_token:
            headers["X-Safety-Token"] = safety_token

        if skip_view_increment:
            url += "?skip_view=true"
            if not safety_token:
                raise ValueError("Cannot skip view counter increment without providing the safety token.")

        with self.session.get(url, headers=headers) as resp:
            if 200 < resp.status_code <= 299:
                err = error_factory(resp.status_code)
                raise err(status_code=resp.status_code, paste_id=paste_id, response=resp)

            data: PasteyGetResponse = resp.json()

        if raw:
            fmt = ""
            for file in data["files"]:
                fmt += file["content"] + "\n\n----\n\n"
            return fmt

        return Paste.from_payload(self, data)

    def create_paste(
        self,
        *,
        files: list[File],
        expires_at: datetime.datetime | None = None,
        password: str | None = None,
        remaining_views: int | None = None,
    ) -> Paste:
        payload = create_payload(files=files, expires_at=expires_at, password=password, remaining_views=remaining_views)

        with self.session.post(f"{self.__base_url__}/pastes", json=payload) as resp:
            if 200 < resp.status_code <= 299:
                err = error_factory(resp.status_code)
                raise err(status_code=resp.status_code, response=resp)

            data: PasteyCreateResponse = resp.json()

        return Paste.from_payload(self, data)

    def delete_paste(self, paste_id: str, safety_token: str) -> None:
        with self.session.delete(f"{self.__base_url__}/pastes/{paste_id}", headers={"X-Safety-Token": safety_token}) as resp:
            if 200 < resp.status_code <= 299:
                err = error_factory(resp.status_code)
                raise err(status_code=resp.status_code, paste_id=paste_id, response=resp)

    def close(self) -> None:
        if self.__owns_session__:
            self.session.close()
