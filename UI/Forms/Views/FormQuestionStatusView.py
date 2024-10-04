from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from Assets import BotEmojis
from Enums import UIComponentType
from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import FormQuestion
################################################################################

__all__ = ("FormQuestionStatusView",)

################################################################################
class FormQuestionStatusView(FroggeView):

    def __init__(self, owner: User, question: FormQuestion):
        
        super().__init__(owner, question)
        
        button_list = [
            ComponentTypeButton(),
            ToggleRequiredButton(),
            PrimaryTextButton(),
            SecondaryTextButton(),
            QuestionPromptMenuButton(),
            AddOptionButton(),
            ModifyOptionButton(),
            RemoveOptionButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class ComponentTypeButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set UI Component Type",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_component_type(interaction)        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ToggleRequiredButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Toggle Required",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.style = (
            ButtonStyle.success
            if self.view.ctx.required
            else ButtonStyle.secondary
        )
        self.emoji = BotEmojis.Check if self.view.ctx.required else None
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.toggle_required(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class PrimaryTextButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Primary Text",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_primary_text(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SecondaryTextButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Secondary Text",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.secondary_text)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_secondary_text(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class QuestionPromptMenuButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Modify Prompt",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.prompt_menu(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class AddOptionButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Select Option",
            row=1
        )
        
    def set_attributes(self) -> None:
        self.disabled = self.view.ctx.ui_type not in (UIComponentType.SelectMenu, UIComponentType.MultiSelect)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_option(interaction)
        self.view.set_button_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ModifyOptionButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Select Option",
            row=1
        )
        
    def set_attributes(self) -> None:
        self.disabled = self.view.ctx.ui_type not in (UIComponentType.SelectMenu, UIComponentType.MultiSelect)

    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_option(interaction)
        self.view.set_button_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveOptionButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Select Option",
            row=1
        )
        
    def set_attributes(self) -> None:
        self.disabled = self.view.ctx.ui_type not in (UIComponentType.SelectMenu, UIComponentType.MultiSelect)

    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_option(interaction)
        self.view.set_button_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
