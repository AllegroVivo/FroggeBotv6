from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import VIPMemberManager
################################################################################

__all__ = ("VIPMemberManagerMenuView",)

################################################################################
class VIPMemberManagerMenuView(FroggeView):

    def __init__(self, owner: User, mgr: VIPMemberManager):
        
        super().__init__(owner, mgr)
        
        button_list = [
            AddMembershipButton(),
            ModifyMembershipButton(),
            RemoveMembershipButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class AddMembershipButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Member",
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
class ModifyMembershipButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Member",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.members) == 0
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_item(interaction)

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveMembershipButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Member",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.members) == 0
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_item(interaction)
        self.view.set_button_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
