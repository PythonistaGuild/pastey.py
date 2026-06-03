from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired

__all__ = (
    "PasteyFile",
    "PasteyFileCreateResponse",
)


class PasteyFile(TypedDict):
    name: NotRequired[str]
    language: NotRequired[str]
    content: str


class PasteyFileCreateResponse(TypedDict):
    id: str
    character_count: int
    line_count: int
    name: str
    language: str
    content: str
