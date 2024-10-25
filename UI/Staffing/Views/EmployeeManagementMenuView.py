from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import User, Interaction, TextChannel, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import StaffManager
################################################################################

__all__ = ("EmployeeManagementMenuView",)

################################################################################
class EmployeeManagementMenuView(FroggeView):

    def __init__(self, owner: User, manager: StaffManager):
        
        super().__init__(owner, manager)
        
        button_list = [
            AddEmployeeButton(),
            ModifyEmployeeButton(),
            RemoveEmployeeButton(),
            # EmployeeReportButton(),
            # EmployeeStatisticsButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class AddEmployeeButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Employee",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_item(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.employee_status(), view=self.view
        )
        
################################################################################
class ModifyEmployeeButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Employee",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_item(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.employee_status(), view=self.view
        )
        
################################################################################
class RemoveEmployeeButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Terminate Employee",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_item(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.employee_status(), view=self.view
        )
        
################################################################################
class EmployeeReportButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Employee Report",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.employee_report(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.employee_status(), view=self.view
        )
        
################################################################################
class EmployeeStatisticsButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Employee Statistics",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.employee_statistics(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.employee_status(), view=self.view
        )
        
################################################################################
