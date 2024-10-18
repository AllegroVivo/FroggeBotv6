from __future__ import annotations

from typing import TYPE_CHECKING, List, Type, TypeVar, Optional

from discord import Interaction

from Errors import MaxItemsReached
from UI.Common import FroggeSelectView, ConfirmCancelView, BasicTextModal
from Utilities import Utilities as U
from .VIPPerk import VIPPerk

if TYPE_CHECKING:
    from Classes import VIPTier, GuildData, FroggeBot
################################################################################

__all__ = ("VIPPerksManager", )

VPM = TypeVar("VPM", bound="VIPPerksManager")

################################################################################
class VIPPerksManager:

    __slots__ = (
        "_parent",
        "_perks",
    )
    
    MAX_ITEMS = 20
    
################################################################################
    def __init__(self, parent: VIPTier) -> None:

        self._parent: VIPTier = parent
        self._perks: List[VIPPerk] = []
    
################################################################################
    @classmethod
    def load(cls: Type[VPM], parent: VIPTier, data: List[dict]) -> VPM:
        
        self: VPM = cls.__new__(cls)
        
        self._parent = parent
        self._perks = [VIPPerk.load(self, perk) for perk in data]
        
        return self
    
################################################################################
    def __getitem__(self, perk_id: int) -> Optional[VIPPerk]:

        return next((perk for perk in self._perks if perk.id == perk_id), None)

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
    def perks(self) -> List[VIPPerk]:
        
        return self._perks
    
################################################################################
    async def add_perk(self, interaction: Interaction) -> None:

        if len(self._perks) >= self.MAX_ITEMS:
            error = MaxItemsReached("VIP Perk", self.MAX_ITEMS)
            await interaction.respond(embed=error, ephemeral=True)
            return

        modal = BasicTextModal(
            title="VIP Perk Text",
            attribute="Text",
            example="e.g. '3 Free Photoshoots'",
            max_length=80,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        new_perk = VIPPerk.new(self)
        self._perks.append(new_perk)
        
        new_perk.text = modal.value
        await new_perk.menu(interaction)

        await self.guild.vip_manager.update_perks_post_components()

################################################################################
    async def modify_perk(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="Modify Perk",
            description="Select the VIP Perk you would like to modify."
        )
        view = FroggeSelectView(interaction.user, [p.select_option() for p in self.perks])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        perk = self[int(view.value)]
        await perk.menu(interaction)

        await self.guild.vip_manager.update_perks_post_components()

################################################################################
    async def remove_perk(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="Remove Perk",
            description="Select the VIP Perk you would like to remove."
        )
        view = FroggeSelectView(interaction.user, [p.select_option() for p in self.perks])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        perk = self[int(view.value)]

        confirm = U.make_embed(
            title="Confirm Deletion",
            description=f"Are you sure you want to delete the VIP Perk `{perk.text}`?"
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        perk.delete()

        await self.guild.vip_manager.update_perks_post_components()

################################################################################
    
