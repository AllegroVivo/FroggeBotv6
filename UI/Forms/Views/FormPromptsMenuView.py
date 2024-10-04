from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import Form
################################################################################

__all__ = ("FormPromptsMenuView",)

################################################################################
class FormPromptsMenuView(FroggeView):

    def __init__(self, owner: User, form: Form):
        
        super().__init__(owner, form)
        
        button_list = [
            SetPreFormPromptButton(),
            SetPostFormPromptButton(),
            CloseMessageButton(),
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class SetPreFormPromptButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Pre-Form Prompt",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.pre_prompt_menu(interaction)        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.prompts_status(), view=self.view
        )
        
################################################################################
class SetPostFormPromptButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Post-Form Prompt",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.post_prompt_menu(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.prompts_status(), view=self.view
        )
        
################################################################################
