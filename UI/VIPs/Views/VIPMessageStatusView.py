from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from Assets import BotEmojis
from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import VIPMessage
################################################################################

__all__ = ("VIPMessageStatusView",)

################################################################################
class VIPMessageStatusView(FroggeView):

    def __init__(self, owner: User, msg: VIPMessage):
        
        super().__init__(owner, msg)
        
        button_list = [
            SetTitleButton(),
            SetDescriptionButton(),
            SetThumbnailButton(),
        ]
        if msg._type.value == 1:
            button_list.append(SetWarningThresholdButton())

        button_list += [
            ToggleActiveButton(msg._type.value == 1),
            CloseMessageButton()
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
class SetWarningThresholdButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Set Warning Threshold",
            disabled=False,
            row=1
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_warning_threshold(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )

################################################################################
class ToggleActiveButton(FroggeButton):
    
    def __init__(self, row1: bool):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Toggle Active",
            disabled=False,
            row=1 if row1 else 0
        )
        
    def set_attributes(self) -> None:
        self.style = ButtonStyle.success if self.view.ctx.is_active else ButtonStyle.danger
        self.emoji = BotEmojis.Check if self.view.ctx.is_active else None
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.toggle_active(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
