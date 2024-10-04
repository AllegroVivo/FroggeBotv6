from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from discord import User, Embed

from Classes.Common import ManagedObject
from .TemplateElement import TemplateElement
from .TemplatePosition import TemplatePosition
from .TemplateShift import TemplateShift

if TYPE_CHECKING:
    from Classes import EventManager
    from UI.Common import FroggeView
################################################################################

__all__ = ("EventTemplate", )

################################################################################
class EventTemplate(ManagedObject):

    __slots__ = (
        "_name",
        "_description",
        "_start_time",
        "_end_time",
        "_image",
        "_secondary_elements",
        "_shifts",
        "_positions",
    )

################################################################################
    def __init__(self, mgr: EventManager, _id: int, **kwargs) -> None:

        super().__init__(mgr, _id)

        self._name: Optional[str] = kwargs.pop("name")
        self._description: Optional[str] = kwargs.pop("description")
        self._start_time: Optional[datetime] = kwargs.pop("start_time")
        self._end_time: Optional[datetime] = kwargs.pop("end_time")
        self._image: Optional[str] = kwargs.pop("image")

        self._secondary_elements: List[TemplateElement] = kwargs.pop("elements")
        self._shifts: List[TemplateShift] = kwargs.pop("shifts")
        self._positions: List[TemplatePosition] = kwargs.pop("positions")

################################################################################
    async def status(self) -> Embed:

        pass

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        pass

################################################################################
