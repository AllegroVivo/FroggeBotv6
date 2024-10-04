from __future__ import annotations

from typing import TYPE_CHECKING, Type, TypeVar, Any, Dict
from discord import SelectOption
from Classes.Common import Identifiable

if TYPE_CHECKING:
    from Classes import EventPosition, StaffMember, ShiftBracket, FroggeBot
################################################################################

__all__ = ("EventSignup", )

ES = TypeVar("ES", bound="EventSignup")

################################################################################
class EventSignup(Identifiable):

    __slots__ = (
        "_parent",
        "_staff",
        "_bracket",
    )

################################################################################
    def __init__(self, parent: EventPosition, _id: int, **kwargs) -> None:

        super().__init__(_id)

        self._parent: EventPosition = parent

        self._staff: StaffMember = kwargs.pop("staff")
        self._bracket: ShiftBracket = kwargs.pop("bracket")

################################################################################
    @classmethod
    def new(cls: Type[ES], parent: EventPosition, staff: StaffMember, bracket: ShiftBracket) -> ES:

        data = parent.bot.api.create_event_signup(parent.id, staff.id, bracket.id)
        return cls(parent, _id=data["id"], staff=staff, bracket=bracket)

################################################################################
    @classmethod
    def load(cls: Type[ES], parent: EventPosition, data: Dict[str, Any]) -> ES:

        return cls(
            parent=parent,
            _id=data["id"],
            staff=parent.parent.manager.guild.staff_manager.get_by_id(data["staff_id"]),
            bracket=parent.parent.get_shift_bracket(data["bracket_id"])
        )

################################################################################
    @property
    def bot(self) -> FroggeBot:

        return self._parent.bot

################################################################################
    @property
    def parent(self) -> EventPosition:

        return self._parent

################################################################################
    @property
    def staff_member(self) -> StaffMember:

        return self._staff

################################################################################
    @property
    def bracket(self) -> ShiftBracket:

        return self._bracket

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_event_signup(self.id)
        self.parent.signups.remove(self)

################################################################################
    def select_option(self) -> SelectOption:

        return SelectOption(
            label=self.staff_member._details.name,
            value=str(self.id),
            description=self.bracket.select_option().label
        )

################################################################################
