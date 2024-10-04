from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Embed

from Classes.Common import LazyChannel
from Classes.Activities import BaseActivity
from .ContestDetails import ContestDetails
from .ContestJudgeManager import ContestJudgeManager
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import ContestManager
    from UI.Common import FroggeView
################################################################################

__all__ = ("Contest", )

################################################################################
class Contest(BaseActivity):

    __slots__ = (
        "_judge_mgr",
        "_channel",
    )

################################################################################
    def __init__(self, mgr: ContestManager, _id: int, **kwargs) -> None:

        details = kwargs.get("details") or ContestDetails(self)
        entries = kwargs.get("entries", [])
        winners = kwargs.get("winners", [])

        super().__init__(mgr, _id, details, entries, winners)

        self._judge_mgr: ContestJudgeManager = ContestJudgeManager(self)
        self._channel: LazyChannel = LazyChannel(self, kwargs.get("channel_id"))

################################################################################
    async def status(self) -> Embed:

        pass

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        pass

################################################################################
