from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Type, TypeVar, Any, Dict

from discord import User, Embed

from Classes.Common import ManagedObject

if TYPE_CHECKING:
    from Classes import PunchManager, StaffMember, Position
    from UI.Common import FroggeView
################################################################################

__all__ = ("Punch", )

P = TypeVar("P", bound="Punch")

################################################################################
class Punch(ManagedObject):

    __slots__ = (
        "_staff",
        "_in"
        "_out",
        "_position",
        "_event_id",
    )
    
################################################################################
    def __init__(self, mgr: PunchManager, _id: int, **kwargs) -> None:

        super().__init__(mgr, _id)

        self._staff: StaffMember = kwargs.pop("staff")
        self._position: Position = kwargs.pop("position")

        self._in: datetime = kwargs.pop("in")
        self._out: Optional[datetime] = kwargs.get("out")

        self._event_id: Optional[int] = kwargs.get("event_id")

################################################################################
    @classmethod
    def new(
        cls: Type[P],
        mgr: PunchManager,
        staff: StaffMember,
        position: Position,
        event_id: Optional[int] = None
    ) -> P:

        # new_data = mgr.bot.api.create_punch(mgr.guild_id, staff.id, position.id, event_id)
        new_data = {
            "id": 0,
            "staff_id": staff.id,
            "position_id": position.id,
            "in": datetime.now(),
            "out": None,
            "event_id": event_id,
        }
        return cls(mgr, new_data["id"], staff=staff, position=position, **new_data)

################################################################################
    @classmethod
    def load(cls: Type[P], mgr: PunchManager, data: Dict[str, Any]) -> P:

        return cls(mgr, _id, **kwargs)

################################################################################
    @property
    def staff(self) -> StaffMember:

        return self._staff

################################################################################
    @property
    def position(self) -> Position:

        return self._position

################################################################################
    @property
    def in_time(self) -> datetime:

        return self._in

################################################################################
    @property
    def out_time(self) -> Optional[datetime]:

        return self._out

################################################################################
    @property
    def event_id(self) -> Optional[int]:

        return self._event_id

################################################################################
    @property
    def duration(self) -> Optional[int]:

        if self._out is None:
            return None

        return (self._out - self._in).seconds

################################################################################
    async def status(self) -> Embed:

        pass

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        pass
    
################################################################################
