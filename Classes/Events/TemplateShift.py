from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Type, TypeVar

from Classes.Common import Identifiable

if TYPE_CHECKING:
    from Classes import EventTemplate, ShiftBracket
################################################################################

__all__ = ("TemplateShift", )

TS = TypeVar("TS", bound="TemplateShift")

################################################################################
class TemplateShift(Identifiable):

    __slots__ = (
        "_parent",
        "_start",
        "_end",
    )

################################################################################
    def __init__(self, parent: EventTemplate, _id: int, **kwargs) -> None:

        super().__init__(_id)

        self._parent: EventTemplate = parent

        self._start: datetime = kwargs.get("start")
        self._end: datetime = kwargs.get("end")

################################################################################
    @classmethod
    def from_shift(cls: Type[TS], parent: EventTemplate, shift: ShiftBracket) -> TS:

        self: TS = cls.__new__(cls)

        self._parent = parent

        self._start = shift.start_time.time()
        self._end = shift.end_time.time()

        self._id = parent.bot.api.create_template_shift(self)

        return self

################################################################################
    @classmethod
    def load(cls: Type[TS], parent: EventTemplate, data: dict) -> TS:

        return cls(
            parent=parent,
            _id=data["id"],
            start=datetime.fromisoformat(data["start_time"]) if data["start_time"] else None,
            end=datetime.fromisoformat(data["end_time"]) if data["end_time"] else None,
        )

################################################################################
    def to_dict(self) -> dict:

        return {
            "parent_id": self._parent.id,
            "start": self._start.isoformat() if self._start else None,
            "end": self._end.isoformat() if self._end else None,
        }

################################################################################
