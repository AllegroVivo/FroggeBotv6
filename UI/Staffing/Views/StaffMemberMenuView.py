from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import StaffMember
################################################################################

__all__ = ("StaffMemberMenuView",)

################################################################################
class StaffMemberMenuView(FroggeView):

    def __init__(self, owner: User, employee: StaffMember):
        
        super().__init__(owner, employee)
        
        button_list = [
            SetNameButton(),
            SetBirthdayButton(),
            SetQualificationsButton(),
            SetNotesButton(),
            ModifyProfileButton(),
            EditEmploymentHistoryButton(),
            TerminateEmploymentButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)

        self.set_button_attributes()
        
################################################################################
class SetNameButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Name",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_name(interaction)        
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetBirthdayButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Birthday",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_birthday(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetQualificationsButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Qualifications",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.disabled = self.view.ctx.is_terminated
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_qualifications(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetNotesButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Notes",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_notes(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ModifyProfileButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Profile",
            disabled=False,
            row=1
        )

    def set_attributes(self) -> None:
        self.disabled = self.view.ctx.is_terminated
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.admin_modify_profile(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class EditEmploymentHistoryButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Edit Employment History",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.edit_employment_history(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class TerminateEmploymentButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Terminate Employee",
            disabled=False,
            row=1
        )

    def set_attributes(self) -> None:
        self.disabled = self.view.ctx.is_terminated
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.terminate(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
