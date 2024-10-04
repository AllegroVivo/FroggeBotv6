from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from discord import User, Embed

from Classes.Common import ManagedObject

if TYPE_CHECKING:
    from Classes import PunchManager, StaffMember, Position
    from UI.Common import FroggeView
################################################################################

__all__ = ("Punch", )

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
    async def status(self) -> Embed:

        pass

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        pass
    
################################################################################
