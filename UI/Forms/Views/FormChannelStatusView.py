from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle, ChannelType

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import Form
################################################################################

__all__ = ("FormChannelStatusView",)

################################################################################
class FormChannelStatusView(FroggeView):

    def __init__(self, owner: User, form: Form):
        
        super().__init__(owner, form)
        
        button_list = [
            AddRoleButton(),
            RemoveRoleButton(),
            ModifyCreateCategoryButton(form.create_type),
            CloseMessageButton(),
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class AddRoleButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Role",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_channel_role(interaction)        
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.channel_status(), view=self.view
        )
        
################################################################################
class RemoveRoleButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Role",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_channel_role(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.channel_status(), view=self.view
        )
        
################################################################################
class ModifyCreateCategoryButton(FroggeButton):
    
    def __init__(self, create_type: ChannelType):

        word = "Category" if create_type == ChannelType.text else "Channel"
        super().__init__(
            style=ButtonStyle.primary,
            label=f"Select Creation {word}",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_category(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.channel_status(), view=self.view
        )
        
################################################################################
