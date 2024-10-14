from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any, Dict, Type, TypeVar, Union

from discord import PartialEmoji

if TYPE_CHECKING:
    from Classes import SymbolMap
################################################################################

__all__ = ("SymbolItem", )

SI = TypeVar("SI", bound="SymbolItem")

################################################################################
class SymbolItem:

    __slots__ = (
        "id",
        "name",
        "unicode",
        "emoji",
        "button_row",
    )

################################################################################
    def __init__(self, data: Dict[str, Any]) -> None:

        self.button_row: int = data["button_row"]

        self.id: Optional[int] = data["id"]
        self.name: Optional[str] = data["name"]
        self.unicode: Optional[str] = data["unicode"]
        self.emoji: Optional[Union[PartialEmoji, str]] = (
            PartialEmoji.from_str(data["emoji"])
            if data.get("emoji") and data.get("emoji").startswith("<") and data.get("emoji").endswith(">")
            else data.get("emoji")
        )

################################################################################
