from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from Utilities.Constants import *
from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import EventDetails
################################################################################

__all__ = ("EventElementMenuView",)

################################################################################
class EventElementMenuView(FroggeView):

    def __init__(self, owner: User, details: EventDetails):
        
        super().__init__(owner, details)
        
        button_list = [
            AddElementButton(),
            ModifyElementButton(),
            RemoveElementButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class AddElementButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Element",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.elements) >= MAX_SECONDARY_ELEMENT_COUNT
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_secondary_element(interaction)
        self.view.set_button_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.secondary_element_status(), view=self.view
        )
        
################################################################################
class ModifyElementButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Element",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.elements) == 0
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_secondary_element(interaction)
        self.view.set_button_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.secondary_element_status(), view=self.view
        )
        
################################################################################
class RemoveElementButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Element",
            row=0
        )

    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.elements) == 0
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_secondary_element(interaction)
        self.view.set_button_attributes()

        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.secondary_element_status(), view=self.view
        )
        
################################################################################
