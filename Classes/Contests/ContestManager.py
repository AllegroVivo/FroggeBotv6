from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from discord import User, Embed

from Classes.Activities import ActivityManager
from .Contest import Contest
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import GuildData
    from UI.Common import FroggeView
################################################################################

__all__ = ("ContestManager", )

################################################################################
class ContestManager(ActivityManager):

    __slots__ = (
        "",
    )

################################################################################
    def __init__(self, state: GuildData) -> None:

        super().__init__(state, Contest)

################################################################################
    async def load_all(self, payload: Dict[str, Any]) -> None:

        pass

################################################################################
    async def status(self) -> Embed:

        return U.make_embed(
            title="__Contest Module Status__",
            description=(
                f"Created Contests: **[`{len(self.active_items)}`]**"
            ),
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        pass

################################################################################
