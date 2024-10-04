from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import User, Interaction, ButtonStyle, Role

from Assets import BotEmojis
from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import VIPTier
################################################################################

__all__ = ("VIPTierStatusView",)

################################################################################
class VIPTierStatusView(FroggeView):

    def __init__(self, owner: User, tier: VIPTier):
        
        super().__init__(owner, tier)
        
        button_list = [
            SetNameButton,
            SetCostButton,
            SetRoleButton,
            ToggleLifetimeButton,
            SetColorButton,
            SetThumbnailButton,
            ChangeOrderButton,
            AddPerkButton,
            ModifyPerkButton,
            RemovePerkButton,
            CloseMessageButton
        ]
        for btn in button_list:
            self.add_item(btn())
            
        self.set_button_attributes()
        
################################################################################
class SetNameButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Name",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.name)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_name(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetRoleButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Role",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx._role.id)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_role(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetCostButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Cost",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.cost)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_cost(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetColorButton(FroggeButton):

    def __init__(self):

        super().__init__(
            label="Set Accent Color",
            disabled=False,
            row=1
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.color)

    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_color(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class ChangeOrderButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Change Display Order",
            disabled=False,
            row=1
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_order(interaction)

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class SetThumbnailButton(FroggeButton):

    def __init__(self):

        super().__init__(
            label="Set Thumbnail",
            disabled=False,
            row=1
        )
        
    def set_attributes(self) -> None:
        self.style = ButtonStyle.primary if self.view.ctx.thumbnail else ButtonStyle.secondary

    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_thumbnail(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class ToggleLifetimeButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Toggle Lifetime",
            disabled=False,
            row=0,
        )
        
    def set_attributes(self) -> None:
        self.style = ButtonStyle.success if self.view.ctx.lifetime else ButtonStyle.secondary
        self.emoji = BotEmojis.Check if self.view.ctx.lifetime else None
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.toggle_lifetime(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class AddPerkButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Perk",
            row=2
        )
        
    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.perks) >= self.view.ctx._perks.MAX_ITEMS
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_perk(interaction)
        self.view.set_button_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ModifyPerkButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Perk",
            row=2
        )

    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.perks) == 0
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_perk(interaction)

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemovePerkButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Perk",
            row=2
        )

    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.perks) == 0

    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_perk(interaction)
        self.view.set_button_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
