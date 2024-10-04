from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import Position
################################################################################

__all__ = ("PositionStatusView",)

################################################################################
class PositionStatusView(FroggeView):

    def __init__(self, owner: User, position: Position):
        
        super().__init__(owner, position)
        
        button_list = [
            SetNameButton(),
            SetRoleButton(),
            SetSalaryButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class SetNameButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Name",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.name)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_name(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetSalaryButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Salary",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.salary)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_salary(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetRoleButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Role",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.set_style(self.view.ctx._role._item_id)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_role(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
