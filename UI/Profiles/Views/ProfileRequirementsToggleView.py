from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from Assets import BotEmojis
from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import ProfileRequirements
################################################################################

__all__ = ("ProfileRequirementsToggleView",)

################################################################################
class ProfileRequirementsToggleView(FroggeView):

    def __init__(self, owner: User, reqs: ProfileRequirements):
        
        super().__init__(owner, reqs)

        for i, attr in enumerate(reqs.__slots__):
            if not attr.startswith("_"):
                self.add_item(ProfileRequirementButton(attr))
        self.add_item(CloseMessageButton())
            
        self.set_button_attributes()
        
################################################################################
class ProfileRequirementButton(FroggeButton):
    
    def __init__(self, attr: str):
        
        super().__init__(
            label=attr.replace("_", " ").title(),
            disabled=False,
        )
        
        self.attr: str = attr
        
    def set_attributes(self) -> None:
        self.style = (
            ButtonStyle.success 
            if getattr(self.view.ctx, self.attr)
            else ButtonStyle.secondary
        )
        self.emoji = (
            BotEmojis.Check 
            if getattr(self.view.ctx, self.attr)
            else None
        )
        
    async def callback(self, interaction: Interaction):
        self.view.ctx.toggle(self.attr)
        self.view.set_button_attributes()
        
        await self.view.dummy_response(interaction)
        await self.view.edit_message_helper(
            interaction=interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
