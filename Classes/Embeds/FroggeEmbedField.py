from __future__ import annotations

from typing import TYPE_CHECKING, Optional, TypeVar, Type, Any, Dict
from discord import EmbedField

from Classes.Common import Identifiable

if TYPE_CHECKING:
    from Classes import FroggeEmbed, FroggeBot
################################################################################

__all__ = ("FroggeEmbedField", )

FEF = TypeVar("FEF", bound="FroggeEmbedField")

################################################################################
class FroggeEmbedField(Identifiable):

    __slots__ = (
        "_parent",
        "_name",
        "_value",
        "_inline",
        "_order",
    )

################################################################################
    def __init__(self, parent: FroggeEmbed, _id: int, order : int, **kwargs) -> None:

        super().__init__(_id)

        self._parent: FroggeEmbed = parent
        self._order: int = order

        self._name: Optional[str] = kwargs.get("name")
        self._value: Optional[str] = kwargs.get("field")
        self._inline: bool = kwargs.get("inline", False)

################################################################################
    @classmethod
    def load(cls: Type[FEF], parent: FroggeEmbed, data: Dict[str, Any]) -> FEF:

        return cls(
            parent=parent,
            _id=data["id"],
            order=data["sort_order"],
            name=data["name"],
            value=data["value"],
            inline=data["inline"]
        )

################################################################################
    @property
    def bot(self) -> FroggeBot:

        return self._parent.bot

################################################################################
    @property
    def name(self) -> Optional[str]:

        return self._name

    @name.setter
    def name(self, value: Optional[str]) -> None:

        self._name = value
        self.update()

################################################################################
    @property
    def value(self) -> Optional[str]:

        return self._value

    @value.setter
    def value(self, value: Optional[str]) -> None:

        self._value = value
        self.update()

################################################################################
    @property
    def inline(self) -> bool:

        return self._inline

    @inline.setter
    def inline(self, value: bool) -> None:

        self._inline = value
        self.update()

################################################################################
    @property
    def order(self) -> int:

        return self._order

    @order.setter
    def order(self, value: int) -> None:

        self._order = value
        self.update()

################################################################################
    def update(self) -> None:

        self.bot.api.update_embed_field(self)

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_embed_field(self.id)
        self._parent.fields.remove(self)

################################################################################
    def to_dict(self) -> dict:

        return {
            "name": self.name,
            "value": self.value,
            "inline": self.inline
        }

################################################################################
    def compile(self) -> EmbedField:

        return EmbedField(
            name=self.name,
            value=self.value,
            inline=self.inline
        )

################################################################################
