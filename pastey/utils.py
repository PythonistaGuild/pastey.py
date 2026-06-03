from __future__ import annotations

import asyncio
import inspect
import os
import sys
from typing import TYPE_CHECKING

from .file import File

if TYPE_CHECKING:
    import datetime

    from types_.file import PasteyFile
    from types_.paste import PasteyPayload

__all__ = ("create_payload", "iscoroutinefunction")

if sys.version_info >= (3, 12):
    iscoroutinefunction = inspect.iscoroutinefunction
else:
    iscoroutinefunction = asyncio.iscoroutinefunction


def base_url() -> str:
    return os.getenv("PASTEY_BASE_URL", "https://api.pastey.gg")


def create_payload(
    *,
    files: list[File] | list[PasteyFile],
    expires_at: datetime.datetime | None = None,
    password: str | None = None,
    remaining_views: int | None = None,
) -> PasteyPayload:
    payload: PasteyPayload = {"files": []}

    for file in files:
        if isinstance(file, File):
            payload["files"].append(file.to_payload())
        else:
            payload["files"].append(file)

    if expires_at:
        payload["expires_at"] = expires_at.isoformat()
    if password:
        payload["password"] = password
    if remaining_views:
        payload["remaining_views"] = remaining_views

    return payload
