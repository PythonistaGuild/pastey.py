from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired

    from .file import PasteyFile, PasteyFileCreateResponse

__all__ = ("PasteyCreateResponse", "PasteyGetResponse", "PasteyPayload")


class PasteyPayload(TypedDict):
    files: list[PasteyFile]
    password: NotRequired[str]
    remaining_views: NotRequired[int]
    expires_at: NotRequired[str]  # isoformat dt


class PasteyGetResponse(TypedDict):
    id: str
    created_at: str
    web: bool
    views: int
    expires_at: str | None
    remaining_views: int | None
    has_password: bool
    files: list[PasteyFileCreateResponse]


class PasteyCreateResponse(PasteyGetResponse):
    safety_token: str
