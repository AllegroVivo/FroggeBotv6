from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import VIPTierManager
################################################################################

__all__ = ("VIPTierManagerMenuView",)

################################################################################
class VIPTierManagerMenuView(FroggeView):

    def __init__(self, owner: User, mgr: VIPTierManager):
        
        super().__init__(owner, mgr)
        
        button_list = [
            AddTierButton(),
            ModifyTierButton(),
            RemoveTierButton(),
            BulkMoveTierButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class AddTierButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Tier",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_item(interaction)
        self.view.set_button_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ModifyTierButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Tier",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.tiers) == 0
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_item(interaction)

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveTierButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Tier",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.tiers) == 0
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_item(interaction)
        self.view.set_button_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class BulkMoveTierButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Bulk Move Member Tier",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.bulk_move_tier(interaction)

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
