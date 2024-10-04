from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import ProfileManager
################################################################################

__all__ = ("ProfileChannelsMenuView",)

################################################################################
class ProfileChannelsMenuView(FroggeView):

    def __init__(self, owner: User, mgr: ProfileManager):
        
        super().__init__(owner, mgr)
        
        button_list = [
            AddChannelGroupButton(),
            ModifyChannelGroupButton(),
            RemoveChannelGroupButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class AddChannelGroupButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Channel Group",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_channel_group(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.channel_status(), view=self.view
        )
        
################################################################################
class ModifyChannelGroupButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Channel Group",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_channel_group(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.channel_status(), view=self.view
        )
        
################################################################################
class RemoveChannelGroupButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Channel Group",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_channel_group(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.channel_status(), view=self.view
        )
        
################################################################################
