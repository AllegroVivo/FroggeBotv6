from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import User, Interaction, ButtonStyle, Role

from Assets import BotEmojis
from UI.Common import FroggeView, CloseMessageButton, FroggeButton
from Enums import Repeatability

if TYPE_CHECKING:
    from Classes import VIPMember
################################################################################

__all__ = ("VIPMemberStatusView",)

################################################################################
class VIPMemberStatusView(FroggeView):

    def __init__(self, owner: User, member: VIPMember):
        
        super().__init__(owner, member)
        
        button_list = [
            SetTierButton(),
            SetEndDateButton(),
            SetNotesButton(),
            RedeemPerksButton(),
            AddMembershipButton(),
            RemoveMemberButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class SetTierButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Membership Tier",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_tier(interaction)
        self.view.set_button_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetEndDateButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set End Date",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.disabled = self.view.ctx.end_date is None
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_end_date(interaction)

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetNotesButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Set Notes",
            disabled=False,
            row=0
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_notes(interaction)

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class RedeemPerksButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Redeem Perk(s)",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_perk_redemptions(interaction)

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class AddMembershipButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Membership Days",
            disabled=False,
            row=1
        )
        
    def set_attributes(self) -> None:
        self.disabled = self.view.ctx.end_date is None
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_membership(interaction)

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveMemberButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove this Member",
            disabled=False,
            row=1
        )
        
    def set_attributes(self) -> None:
        
        self.disabled = self.view.ctx.end_date is None
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove(interaction)

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
