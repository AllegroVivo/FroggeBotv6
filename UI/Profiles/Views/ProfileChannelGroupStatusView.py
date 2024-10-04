from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Interaction, User, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import ProfileChannelGroup
################################################################################

__all__ = ("ProfileChannelGroupStatusView",)

################################################################################        
class ProfileChannelGroupStatusView(FroggeView):

    def __init__(self, user: User, channel_group: ProfileChannelGroup):

        super().__init__(user, channel_group)

        button_list = [
            AddChannelButton(),
            RemoveChannelButton(),
            AddRoleButton(),
            RemoveRoleButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()

################################################################################        
class AddChannelButton(FroggeButton):

    def __init__(self) -> None:

        super().__init__(
            style=ButtonStyle.success,
            label="Add Posting Channel",
            disabled=False,
            row=0
        )

    async def callback(self, interaction: Interaction) -> None:
        await self.view.ctx.add_channel(interaction)
        await self.view.edit_message_helper(
            interaction=interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class RemoveChannelButton(FroggeButton):
    
    def __init__(self) -> None:
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Channel",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction) -> None:
        await self.view.ctx.remove_channel(interaction)
        await self.view.edit_message_helper(
            interaction=interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class AddRoleButton(FroggeButton):
    
    def __init__(self) -> None:
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Linked Role",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction) -> None:
        await self.view.ctx.add_role(interaction)
        await self.view.edit_message_helper(
            interaction=interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveRoleButton(FroggeButton):
    
    def __init__(self) -> None:
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Role",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction) -> None:
        await self.view.ctx.remove_role(interaction)
        await self.view.edit_message_helper(
            interaction=interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
