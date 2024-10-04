from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from Utilities.Constants import *
from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import StaffableEvent
################################################################################

__all__ = ("ShiftBracketMenuStatusView",)

################################################################################
class ShiftBracketMenuStatusView(FroggeView):

    def __init__(self, owner: User, event: StaffableEvent):
        
        super().__init__(owner, event)
        
        button_list = [
            AddShiftButton(),
            ModifyShiftButton(),
            RemoveShiftButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class AddShiftButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Shift",
            row=0
        )

    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.shifts) >= MAX_SHIFT_BRACKET_COUNT
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_shift_bracket(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ModifyShiftButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Shift",
            row=0
        )
        
    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.shifts) == 0
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_shift_bracket(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveShiftButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Shift",
            row=0
        )

    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.shifts) == 0
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_shift_bracket(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
