from __future__ import annotations

from typing import TYPE_CHECKING, Type, TypeVar

from discord import SelectOption, User, Embed

from Classes.Common import ManagedObject

if TYPE_CHECKING:
    from Classes import VerificationManager
    from UI.Common import FroggeView
################################################################################

__all__ = ("VerificationData", )

VD = TypeVar("VD", bound="VerificationData")

################################################################################
class VerificationData(ManagedObject):

    __slots__ = (
        "_user_id",
        "_name",
        "_lodestone_id",
    )
    
################################################################################
    def __init__(self, mgr: VerificationManager, _id: int, **kwargs) -> None:

        super().__init__(mgr, _id)
        
        self._user_id: int = kwargs.pop("user_id")
        self._name: str = kwargs.pop("name")
        self._lodestone_id: int = kwargs.pop("lodestone_id")
    
################################################################################
    @classmethod
    def new(cls: Type[VD], mgr: VerificationManager, user: User, name: str, lodestone_id: int) -> VD:
        
        verification = mgr.bot.api.create_user_verification(mgr.guild_id, user.id, name, lodestone_id)
        return cls(
            _id=verification["id"],
            mgr=mgr,
            user_id=verification["user_id"],
            name=verification["name"],
            lodestone_id=verification["lodestone_id"]
        )
    
################################################################################
    @classmethod
    def load(cls: Type[VD], mgr: VerificationManager, data: dict) -> VD:

        return cls(
            mgr=mgr,
            _id=data["id"],
            user_id=data["user_id"],
            name=data["name"],
            lodestone_id=data["lodestone_id"]
        )

################################################################################
    def status(self) -> Embed:

        pass

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        pass

################################################################################
