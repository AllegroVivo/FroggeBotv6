from __future__ import annotations

from typing import TYPE_CHECKING, List, Any, Dict

from discord import Interaction, User, Embed

from Classes.Common import ManagedObject
from UI.Common import FroggeView
from .SymbolItem import SymbolItem

if TYPE_CHECKING:
    from Classes import MessageBuilder
################################################################################

__all__ = ("SymbolMap",)

################################################################################
class SymbolMap:

    __slots__ = (
        "name",
        "items",
    )

################################################################################
    def __init__(self, data: Dict[str, Any]) -> None:

        self.name: str = data["name"]
        self.items: List[SymbolItem] = [SymbolItem(item) for item in data["items"]]

################################################################################
