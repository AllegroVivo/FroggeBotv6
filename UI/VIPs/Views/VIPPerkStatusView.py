from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import User, Interaction, ButtonStyle, Role

from Assets import BotEmojis
from UI.Common import FroggeView, CloseMessageButton, FroggeButton
from Enums import Repeatability

if TYPE_CHECKING:
    from Classes import VIPPerk
################################################################################

__all__ = ("VIPPerkStatusView",)

################################################################################
class VIPPerkStatusView(FroggeView):

    def __init__(self, owner: User, perk: VIPPerk):
        
        super().__init__(owner, perk)
        
        button_list = [
            SetTextButton(),
            SetDescriptionButton(),
            SetRepeatabilityButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class SetTextButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Perk Text",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.text)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_text(interaction)
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
        self.set_style(self.view.ctx.description)

        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetRepeatabilityButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Set Repeatability",
            disabled=False,
            row=0
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_repeatability(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )

################################################################################
