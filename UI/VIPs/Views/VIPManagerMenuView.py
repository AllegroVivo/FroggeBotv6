from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import VIPManager
################################################################################

__all__ = ("VIPManagerMenuView",)

################################################################################
class VIPManagerMenuView(FroggeView):

    def __init__(self, owner: User, mgr: VIPManager):
        
        super().__init__(owner, mgr)
        
        button_list = [
            TierManagementButton(),
            MemberManagementButton(),
            WarningMsgManagementButton(),
            PostVIPListButton(),
            PostVIPPerksButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class TierManagementButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Tier Management",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.tier_management(interaction)
        
################################################################################
class MemberManagementButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Member Management",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.member_management(interaction)
        
################################################################################
class WarningMsgManagementButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Renewal/Expiry Message Management",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.message_management(interaction)
        
################################################################################
class PostVIPListButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Post VIP List",
            disabled=False,
            row=2
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.post_vip_list(interaction)
        
################################################################################
class PostVIPPerksButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Post VIP Perks Message",
            disabled=False,
            row=2
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.post_vip_perks_message(interaction)
        
################################################################################
