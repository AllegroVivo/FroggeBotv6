from __future__ import annotations

from typing import TYPE_CHECKING, Union

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import FormPrompt, FormQuestionPrompt
################################################################################

__all__ = ("FormPromptStatusView",)

################################################################################
class FormPromptStatusView(FroggeView):

    def __init__(self, owner: User, prompt: Union[FormPrompt, FormQuestionPrompt]):
        
        super().__init__(owner, prompt)
        
        button_list = [
            SetTitleButton(),
            SetDescriptionButton(),
            SetThumbnailButton(),
            ToggleCancelButton(),
            CloseMessageButton(),
            RemovePromptButton(),
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class SetTitleButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Title",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_title(interaction)        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetThumbnailButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Thumbnail",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_thumbnail(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetDescriptionButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Description",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_description(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ToggleCancelButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.style = (
            ButtonStyle.success
            if self.view.ctx.show_cancel 
            else ButtonStyle.secondary
        )
        self.label = (
            "Show Cancel: ON"
            if self.view.ctx.show_cancel
            else "Show Cancel: OFF"
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.toggle_cancel_button(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemovePromptButton(FroggeButton):

    def __init__(self):

        super().__init__(
            disabled=False,
            row=4
        )

    def set_attributes(self) -> None:
        self.label = (
            "Activate Prompt"
            if not self.view.ctx.is_active
            else "Deactivate Prompt"
        )
        self.style = (
            ButtonStyle.success
            if not self.view.ctx.is_active
            else ButtonStyle.danger
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.toggle_is_active(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )

################################################################################
