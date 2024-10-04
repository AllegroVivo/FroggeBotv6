from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from Assets import BotEmojis

if TYPE_CHECKING:
    from Classes import Profile, FroggeBot, GuildData
################################################################################

__all__ = ("ProfileSection",)

################################################################################
class ProfileSection:
    
    __slots__ = (
        "_parent",
    )

################################################################################
    def __init__(self, parent: Profile) -> None:
        
        self._parent: Profile = parent
        
################################################################################
    @property
    def bot(self) -> FroggeBot:
        
        return self._parent.bot
    
################################################################################
    @property
    def guild(self) -> GuildData:
        
        return self._parent.guild
    
################################################################################
    @property
    def parent(self) -> Profile:
        
        return self._parent
    
################################################################################
    @property
    def profile_id(self) -> int:
        
        return self._parent.id
    
################################################################################
    @staticmethod
    def progress_emoji(attribute: Optional[Any]) -> str:

        return str(BotEmojis.CheckGray) if not attribute else str(BotEmojis.CheckGreen)

################################################################################
