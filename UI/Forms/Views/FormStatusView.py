from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from Assets import BotEmojis
from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import StaffApplicationManager
################################################################################

__all__ = ("FormStatusView",)

################################################################################
class FormStatusView(FroggeView):

    def __init__(self, owner: User, manager: StaffApplicationManager):
        
        super().__init__(owner, manager)
        
        button_list = [
            AddQuestionButton(),
            ModifyQuestionButton(),
            RemoveQuestionButton(),
            ModifyPromptsButton(),
            ViewResponsesButton(),
            SetToNotifyButton(),
            SetChannelButton(),
            SetPostOptionsButton(),
            ToggleCreateChannelButton(),
            ManageChannelButton(),
            CloseMessageButton(),
            PostFormButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class AddQuestionButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Question",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_question(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ModifyQuestionButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Question",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_question(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveQuestionButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Question",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_question(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ModifyPromptsButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Pre/Post Prompts",
            disabled=False,
            row=1
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.prompts_menu(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class SetToNotifyButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Set Notifications",
            disabled=False,
            row=2
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.notifications_menu(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class SetChannelButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Log Channel",
            disabled=False,
            row=2
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
class ViewResponsesButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="View All Responses",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.paginate_responses(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ToggleCreateChannelButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Toggle Create Channel",
            disabled=False,
            row=3
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.toggle_create_channel(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ManageChannelButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Manage Channel Creation",
            disabled=False,
            row=3
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.manage_channel(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetPostOptionsButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Set Posting Options",
            disabled=False,
            row=2
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.post_options_menu(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class PostFormButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Post Form",
            disabled=False,
            row=4
        )

    def set_attributes(self) -> None:
        self.emoji = (
            BotEmojis.Cross
            if self.view.ctx._post_msg.id is None
            else BotEmojis.CheckGreen
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.post(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
