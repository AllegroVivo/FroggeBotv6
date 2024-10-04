from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import ReactionRoleManager
################################################################################

__all__ = ("ReactionRoleManagerMenuView",)

################################################################################
class ReactionRoleManagerMenuView(FroggeView):

    def __init__(self, owner: User, mgr: ReactionRoleManager):
        
        super().__init__(owner, mgr)
        
        button_list = [
            AddRoleMessageButton(),
            ModifyRoleMessageButton(),
            RemoveRoleMessageButton(),
            SetChannelButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)

        self.set_button_attributes()
        
################################################################################
class AddRoleMessageButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Reaction Role",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_item(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ModifyRoleMessageButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Reaction Role",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_item(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveRoleMessageButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Reaction Role",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_item(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetChannelButton(FroggeButton):

    def __init__(self):

        super().__init__(
            label="Set Reaction Role Post Channel",
            disabled=False,
            row=1
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx._channel.id)

    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_channel(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
