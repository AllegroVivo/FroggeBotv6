from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import FormOption
################################################################################

__all__ = ("FormOptionStatusView",)

################################################################################
class FormOptionStatusView(FroggeView):

    def __init__(self, owner: User, option: FormOption):
        
        super().__init__(owner, option)
        
        button_list = [
            SetLabelButton(),
            SetEmojiButton(),
            SetValueButton(),
            SetDescriptionButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class SetLabelButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Label",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.label)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_label(interaction)    
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetDescriptionButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Description",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.description)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_description(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetValueButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Value",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.value)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_value(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetEmojiButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Emoji",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.emoji)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_emoji(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
