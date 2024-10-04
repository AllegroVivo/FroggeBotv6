from __future__ import annotations

from typing import TYPE_CHECKING, Type, TypeVar

from Classes.Common import Identifiable

if TYPE_CHECKING:
    from Classes import EventTemplate, EventPosition
################################################################################

__all__ = ("TemplatePosition", )

TP = TypeVar("TP", bound="TemplatePosition")

################################################################################
class TemplatePosition(Identifiable):

    __slots__ = (
        "_parent",
        "_pos_id",
        "_qty",
    )

################################################################################
    def __init__(self, parent: EventTemplate, _id: int, **kwargs) -> None:

        super().__init__(_id)

        self._parent: EventTemplate = parent

        self._pos_id: int = kwargs.pop("position_id")
        self._qty: int = kwargs.pop("qty")

################################################################################
    @classmethod
    def from_event_pos(cls: Type[TP], parent: EventTemplate, event_pos: EventPosition) -> TP:

        self: TP = cls.__new__(cls)

        self._parent = parent

        self._pos_id = event_pos.position.id
        self._qty = event_pos.quantity

        self._id = parent.bot.api.create_template_position(self)

        return self

################################################################################
    @classmethod
    def load(cls: Type[TP], parent: EventTemplate, data: dict) -> TP:

        return cls(
            parent=parent,
            _id=data["id"],
            position_id=data["position_id"],
            qty=data["quantity"],
        )

################################################################################
    def to_dict(self) -> dict:

        return {
            "template_id": self._parent.id,
            "position_id": self._pos_id,
            "quantity": self._qty,
        }

################################################################################
