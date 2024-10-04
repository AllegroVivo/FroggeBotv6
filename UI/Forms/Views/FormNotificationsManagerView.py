from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import FormNotificationsManager
################################################################################

__all__ = ("FormNotificationsManagerView",)

################################################################################
class FormNotificationsManagerView(FroggeView):

    def __init__(self, owner: User, mgr: FormNotificationsManager):
        
        super().__init__(owner, mgr)
        
        button_list = [
            AddRoleButton(),
            RemoveRoleButton(),
            AddUserButton(),
            RemoveUserButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class AddRoleButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Role to Notify",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_role(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveRoleButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Role to Notify",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_role(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class AddUserButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.success,
            label="Add User to Notify",
            disabled=False,
            row=1
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_user(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class RemoveUserButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.danger,
            label="Remove User to Notify",
            disabled=False,
            row=1
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_user(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
