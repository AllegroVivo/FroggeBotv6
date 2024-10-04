from __future__ import annotations

from typing import TYPE_CHECKING, Any

from discord import Interaction, User, Embed

from Classes.Common import ObjectManager
from Utilities.Constants import DEFAULT_CLOCK_THRESHOLD_MINUTES

if TYPE_CHECKING:
    from Classes import GuildData, EventManager
    from UI.Common import FroggeView
################################################################################

__all__ = ("PunchManager", )

################################################################################
class PunchManager(ObjectManager):

    __slots__ = (
        "_threshold",
    )

################################################################################
    def __init__(self, state: GuildData) -> None:

        super().__init__(state)

        self._threshold: int = DEFAULT_CLOCK_THRESHOLD_MINUTES

################################################################################
    async def load_all(self, payload: Any) -> None:

        pass

################################################################################
    @property
    def event_manager(self) -> EventManager:

        return self._state.event_manager

################################################################################
    async def status(self) -> Embed:

        pass

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        pass

################################################################################
    async def add_item(self, interaction: Interaction) -> None:

        pass

################################################################################
    async def modify_item(self, interaction: Interaction) -> None:

        pass

################################################################################
    async def remove_item(self, interaction: Interaction) -> None:

        pass

################################################################################
    async def clock_in(self, interaction: Interaction) -> None:

        pass

################################################################################
    async def clock_out(self, interaction: Interaction) -> None:

        pass

################################################################################
