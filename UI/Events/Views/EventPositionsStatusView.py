from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from Utilities.Constants import *
from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import StaffableEvent
################################################################################

__all__ = ("EventPositionsStatusView",)

################################################################################
class EventPositionsStatusView(FroggeView):

    def __init__(self, owner: User, event: StaffableEvent):
        
        super().__init__(owner, event)
        
        button_list = [
            AddPositionButton(),
            ModifyPositionButton(),
            RemovePositionButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class AddPositionButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Position",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_position(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ModifyPositionButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Position",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.disabled = not self.view.ctx.positions
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_position(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemovePositionButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Position",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.disabled = not self.view.ctx.positions
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_position(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
