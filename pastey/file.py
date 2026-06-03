from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types_.file import PasteyFile, PasteyFileCreateResponse
    from typing_extensions import Self
__all__ = ("File",)


class File:
    __slots__ = ("character_count", "content", "id", "language", "line_count", "name")

    def __init__(
        self,
        *,
        content: str,
        name: str | None = None,
        language: str | None = None,
        id_: str | None = None,
        character_count: int | None = None,
        line_count: int | None = None,
    ) -> None:
        self.id: str | None = id_
        self.name = name
        self.content = content
        self.language = language
        self.character_count: int = character_count or len(content)
        self.line_count: int = line_count or (content.count("\n") + 1)

    def __repr__(self) -> str:
        return (
            f"<File id={self.id} name={self.name} language={self.language} "
            f"character_count={self.character_count} line_count={self.line_count}>"
        )

    @classmethod
    def from_payload(cls, data: PasteyFileCreateResponse) -> Self:
        return cls(
            content=data["content"],
            name=data.get("name"),
            language=data.get("language"),
            id_=data.get("id"),
            character_count=data.get("character_count"),
            line_count=data.get("line_count"),
        )

    def to_payload(self) -> PasteyFile:
        ret: PasteyFile = {"content": self.content}
        if self.name:
            ret["name"] = self.name
        if self.language:
            ret["language"] = self.language

        return ret
