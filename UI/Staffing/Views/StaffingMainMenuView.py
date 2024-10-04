from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import User, Interaction, TextChannel, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import StaffManager
################################################################################

__all__ = ("StaffingMainMenuView",)

################################################################################
class StaffingMainMenuView(FroggeView):

    def __init__(self, owner: User, manager: StaffManager):
        
        super().__init__(owner, manager)
        
        button_list = [
            EmployeeManagementButton(),
            PositionsMenuButton(),
            SetStaffRoleButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class EmployeeManagementButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Employee Management",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.employee_management_menu(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class PositionsMenuButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Positions Management",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.positions_main_menu(interaction)
        
################################################################################
class SetStaffRoleButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Staff Role",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.set_style(self.view.ctx._staff_role.id)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_staff_role(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
