from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

from discord import Interaction, User, Embed

from .ContestJudge import ContestJudge

if TYPE_CHECKING:
    from Classes import Contest
    from UI.Common import FroggeView
################################################################################

__all__ = ("ContestJudgeManager", )

################################################################################
class ContestJudgeManager:

    __slots__ = (
        "_parent",
        "_judges",
    )

################################################################################
    def __init__(self, parent: Contest, **kwargs) -> None:

        self._parent: Contest = parent
        self._judges: List[ContestJudge] = kwargs.get("judges", [])

################################################################################
    async def load_all(self, payload: Any) -> None:

        pass

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
