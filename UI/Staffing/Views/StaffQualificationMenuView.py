from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import StaffQualifications
################################################################################

__all__ = ("StaffQualificationMenuView",)

################################################################################
class StaffQualificationMenuView(FroggeView):

    def __init__(self, owner: User, qualifications: StaffQualifications):
        
        super().__init__(owner, qualifications)
        
        button_list = [
            AddQualificationButton(),
            RemoveQualificationButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)

        self.set_button_attributes()
        
################################################################################
class AddQualificationButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Qualification(s)",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_qualifications(interaction)        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveQualificationButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Qualification(s)",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.disabled = not self.view.ctx.positions
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_qualifications(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
