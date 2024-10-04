from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from Utilities.Constants import *
from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import Event
################################################################################

__all__ = ("EventStaffManagementView",)

################################################################################
class EventStaffManagementView(FroggeView):

    def __init__(self, owner: User, event: Event):
        
        super().__init__(owner, event)
        
        button_list = [
            AddStaffButton(),
            # ModifyStaffButton(),
            RemoveStaffButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class AddStaffButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Staff",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_staff_manual(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.staff_member_status(), view=self.view
        )
        
################################################################################
class ModifyStaffButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Staff",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.disabled = not self.view.ctx.positions
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_staff_manual(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.staff_member_status(), view=self.view
        )
        
################################################################################
class RemoveStaffButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Staff",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.disabled = not self.view.ctx.positions
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_staff_manual(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.staff_member_status(), view=self.view
        )
        
################################################################################
