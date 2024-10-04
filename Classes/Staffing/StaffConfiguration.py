from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from Classes import StaffMember
################################################################################

__all__ = ("StaffConfiguration", )

################################################################################
class StaffConfiguration:

    __slots__ = (
        "_parent",
        "_shift_pings",
    )

################################################################################
    def __init__(self, parent: StaffMember, **kwargs) -> None:

        self._parent: StaffMember = parent

        self._shift_pings: bool = kwargs.get("shift_pings", True)

################################################################################
    @classmethod
    def load(cls, parent: StaffMember, data: Dict[str, Any]) -> StaffConfiguration:

        return cls(parent, shift_pings=data["shift_pings"])

################################################################################
