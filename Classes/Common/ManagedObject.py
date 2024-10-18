from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from discord import Interaction, Embed, User, SelectOption

from .FroggeObject import FroggeObject
from Enums import Timezone
from logger import log
from UI.Common import BasicTextModal, ConfirmCancelView
from Utilities import Utilities as U
from .Identifiable import Identifiable

if TYPE_CHECKING:
    from Classes import ObjectManager, FroggeBot, GuildData
    from UI.Common import FroggeView
################################################################################

__all__ = ("ManagedObject",)

################################################################################
class ManagedObject(Identifiable, FroggeObject):

    __slots__ = (
        "_mgr",
    )
    
################################################################################
    def __init__(self, mgr: ObjectManager, _id: int) -> None:
        
        super().__init__(_id)
        FroggeObject.__init__(self)
        
        self._mgr: ObjectManager = mgr
    
################################################################################
    @property
    def bot(self) -> FroggeBot:
        
        return self._mgr.bot
    
################################################################################
    @property
    def guild(self) -> GuildData:
        
        return self._mgr.guild
    
################################################################################
    @property
    def guild_id(self) -> int:
        
        return self.guild_id
    
################################################################################
    @property
    def manager(self) -> ObjectManager:
        
        return self._mgr
    
################################################################################
    @property
    def timezone(self) -> Timezone:
        
        return self.manager.guild.config.timezone
    
    @property
    def py_tz(self):
        
        return U.TIMEZONE_OFFSETS[self.timezone]
    
################################################################################
    @abstractmethod
    async def status(self) -> Embed:
        
        raise NotImplementedError
    
################################################################################
    @abstractmethod
    def get_menu_view(self, user: User) -> FroggeView:
        
        raise NotImplementedError
    
################################################################################
    def select_option(self) -> SelectOption:
        
        raise NotImplementedError
    
################################################################################
    async def menu(self, interaction: Interaction) -> None:

        embed = await self.status()
        view = self.get_menu_view(interaction.user)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

        if getattr(self, "update_post_components", None):
            await self.update_post_components()  # type: ignore
        
################################################################################
    async def remove(self, interaction: Interaction) -> None:

        type_name = self.__class__.__name__
        log.info(self.guild, f"Removing {type_name}.")

        prompt = U.make_embed(
            title=f"Remove ",
            description=(
                f"Are you sure you want to remove this {type_name}?"
            )
        )
        view = ConfirmCancelView(interaction.user)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            log.debug(self.guild, f"{type_name} removal cancelled.")
            return
        
        self.delete()

        log.info(self.guild, f"{type_name} removed.")
        
################################################################################
