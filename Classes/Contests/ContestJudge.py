from __future__ import annotations

from typing import TYPE_CHECKING, Dict

from Classes.Common import Identifiable, LazyUser

if TYPE_CHECKING:
    from Classes import ContestJudgeManager
################################################################################

__all__ = ("ContestJudge", )

################################################################################
class ContestJudge(Identifiable):

    __slots__ = (
        "_mgr",
        "_user",
        "_ratings",
    )

################################################################################
    def __init__(self, mgr: ContestJudgeManager, _id: int, **kwargs) -> None:

        super().__init__(_id)

        self._mgr: ContestJudgeManager = mgr

        self._user: LazyUser = LazyUser(self, kwargs.get("user_id"))
        self._ratings: Dict[int, int] = kwargs.get("ratings", {})

################################################################################
