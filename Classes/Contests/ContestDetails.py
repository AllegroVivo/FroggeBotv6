from __future__ import annotations

from typing import TYPE_CHECKING, Type, Tuple, Any, TypeVar

from Classes.Activities import ActivityDetails

if TYPE_CHECKING:
    from Classes import Contest
################################################################################

__all__ = ("ContestDetails", )

CD = TypeVar("CD", bound="ContestDetails")

################################################################################
class ContestDetails(ActivityDetails):

    def __init__(self, parent: Contest, **kwargs) -> None:

        super().__init__(parent, **kwargs)

################################################################################
    @classmethod
    def load(cls: Type[CD], parent: Contest, data: Tuple[Any, ...]) -> CD:

        pass

################################################################################
    def update(self) -> None:

        pass

################################################################################
