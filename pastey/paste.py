from __future__ import annotations

import asyncio
import datetime
import logging
from typing import TYPE_CHECKING

import aiohttp

from .file import File
from .utils import base_urls, create_payload, iscoroutinefunction

if TYPE_CHECKING:
    from types_.paste import PasteyCreateResponse, PasteyGetResponse
    from typing_extensions import Self

    from .client import Client, SyncClient

LOGGER = logging.getLogger(__name__)

__all__ = ("Paste", "create_paste", "create_paste_sync", "delete_paste", "delete_paste_sync")


class Paste:
    def __init__(self, client: Client | SyncClient | None, data: PasteyCreateResponse | PasteyGetResponse) -> None:
        self.client: Client | SyncClient | None = client
        self.id: str = data["id"]
        self.created_at: datetime.datetime = datetime.datetime.strptime(data["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=datetime.timezone.utc
        )
        expires_: str | None = data.get("expires_at")
        self.expires_at: datetime.datetime | None = (
            datetime.datetime.strptime(expires_, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=datetime.timezone.utc)
            if expires_
            else None
        )
        self.views: int = data["views"]
        self.remaining_views: int | None = data["remaining_views"]
        self.has_password: bool = data["has_password"]
        self.files: list[File] = [File.from_payload(file) for file in data["files"]]
        self.safety_token: str | None = data.get("safety_token")

    def __repr__(self) -> str:
        return f"<Paste id={self.id} file_count={len(self.files)} views={self.views}>"

    def __str__(self) -> str:
        return self.url

    @classmethod
    def from_payload(cls, client: Client | SyncClient | None, data: PasteyCreateResponse | PasteyGetResponse) -> Self:
        return cls(client, data)

    @property
    def url(self) -> str:
        base = base_urls().frontend
        return f"{base}/{self.id}"

    def find_file(self, file_id: str | None = None, file_name: str | None = None) -> File | None:
        if not file_id and not file_name:
            raise ValueError("Either `file_id` or `file_name` is required.")

        ret = None
        for file in self.files:
            if (file_id and file.id == file_id) or (file_name and file.name == file_name):
                ret = file

        return ret

    def delete(self) -> None:
        LOGGER.warning(
            "This method is a best-effort async<>sync method to delete a paste. "
            "It is recommend to use your `.delete_paste` method within the client instead."
        )

        if not self.client:
            raise ValueError(
                "Paste was not created via a Client obj, unable to delete the paste via this method. "
                "Please use the `Client.delete_paste` method instead."
            )

        if not self.safety_token:
            raise ValueError("Paste was not created with a safety token, unable to delete unless one is set.")

        if iscoroutinefunction(self.client.delete_paste):
            asyncio.create_task(self.client.delete_paste(self.id, self.safety_token))  # pyright: ignore[reportGeneralTypeIssues] # guarded  # noqa: RUF006 # we dont care about the result
            return None
        return self.client.delete_paste(self.id, self.safety_token)  # pyright: ignore[reportReturnType] # guarded


async def create_paste(
    *,
    base_url: str = "https://api.pastey.gg",
    files: list[File] | None = None,
    content: str | None = None,
    password: str | None = None,
    remaning_views: int | None = None,
    expires_at: datetime.datetime | None = None,
) -> Paste:
    if not files and not content:
        raise ValueError("`files` or `content` must be provided.")

    if files:
        payload = create_payload(files=files, password=password, remaining_views=remaning_views, expires_at=expires_at)
    else:
        # content
        file = File(content=content)  # pyright: ignore[reportArgumentType] # guarded above
        payload = create_payload(files=[file], password=password, remaining_views=remaning_views, expires_at=expires_at)

    async with aiohttp.ClientSession() as session, session.post(f"{base_url}/pastes", json=payload) as resp:
        resp.raise_for_status()
        data = await resp.json()

    return Paste.from_payload(None, data)


def create_paste_sync() -> Paste: ...


async def delete_paste() -> bool: ...


def delete_paste_sync() -> bool: ...
