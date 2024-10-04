from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar

from Enums import RedemptionLevel

if TYPE_CHECKING:
    from Classes import VIPMember, VIPPerk
################################################################################

__all__ = ("VIPPerkOverride", )

VPO = TypeVar("VPO", bound="VIPPerkOverride")

################################################################################
class VIPPerkOverride:

    __slots__ = (
        "_id",
        "_parent",
        "_perk",
        "_level",
    )
    
################################################################################
    def __init__(self, parent: VIPMember, _id: int, **kwargs) -> None:

        self._id: int = _id
        self._parent: VIPMember = parent
        
        self._perk: VIPPerk = kwargs.pop("perk")
        self._level: RedemptionLevel = kwargs.get("level", RedemptionLevel.FullyRedeemed)
    
################################################################################
    @classmethod
    def new(cls: Type[VPO], parent: VIPMember, perk: VIPPerk, level: RedemptionLevel) -> VPO:
        
        new_override = parent.bot.api.create_vip_perk_override(parent.id, perk.id, level.value)
        return cls(parent, new_override["id"], perk=perk, level=level)
    
################################################################################
    @classmethod
    def load(cls: Type[VPO], parent: VIPMember, data: Dict[str, Any]) -> VPO:
        
        return cls(
            parent=parent,
            _id=data["id"],
            perk=parent.guild.vip_manager.get_perk(data["perk_id"]),
            level=RedemptionLevel(data["level"])
        )
    
################################################################################
    @property
    def id(self) -> int:
        
        return self._id
    
################################################################################
    @property
    def perk(self) -> VIPPerk:
        
        return self._perk
    
################################################################################
    @property
    def level(self) -> RedemptionLevel:
        
        return self._level
    
    @level.setter
    def level(self, value: RedemptionLevel) -> None:
        
        self._level = value
        self.update()
        
################################################################################
    def update(self) -> None:
        
        self._parent.bot.api.update_vip_perk_override(self)
        
################################################################################
    def delete(self) -> None:
        
        self._parent.bot.api.delete_vip_perk_override(self)
        
################################################################################
    def to_dict(self) -> Dict[str, Any]:
        
        return {
            "level": self._level.value
        }
    
################################################################################

