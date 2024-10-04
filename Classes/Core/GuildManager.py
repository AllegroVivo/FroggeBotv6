from __future__ import annotations

from discord import Guild
from typing import TYPE_CHECKING, List

from .GuildData import GuildData

if TYPE_CHECKING:
    from Classes import FroggeBot
################################################################################

__all__ = ("GuildManager",)

################################################################################
class GuildManager:

    __slots__ = (
        "_state",
        "_fguilds"
    )
    
################################################################################
    def __init__(self, bot: FroggeBot):
        
        self._state: FroggeBot = bot
        self._fguilds: List[GuildData] = []
    
################################################################################
    def __getitem__(self, guild_id: int) -> GuildData:
        
        for frogge in self._fguilds:
            if frogge.guild_id == guild_id:
                return frogge
    
################################################################################
    def __iter__(self):
        
        return iter(self._fguilds)
    
################################################################################
    @property
    def bot(self) -> FroggeBot:
        
        return self._state
    
################################################################################    
    @property
    def fguilds(self) -> List[GuildData]:
        
        return self._fguilds
    
################################################################################
    def init_guild(self, guild: Guild) -> GuildData:
        
        frogge_guild = GuildData(self.bot, guild)
        self._fguilds.append(frogge_guild)
        
        return frogge_guild
    
################################################################################
