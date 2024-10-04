from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import ProfilePersonality
################################################################################

__all__ = ("ProfilePersonalityStatusView",)

################################################################################
class ProfilePersonalityStatusView(FroggeView):

    def __init__(self, owner: User, personality: ProfilePersonality):
        
        super().__init__(owner, personality)
        
        button_list = [
            LikesButton(),
            DislikesButton(),
            PersonalityButton(),
            AboutMeButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class LikesButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Likes",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.likes)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_likes(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class DislikesButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Dislikes",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.dislikes)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_dislikes(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class PersonalityButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Personality",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.personality)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_personality(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class AboutMeButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="About Me",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.aboutme)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_aboutme(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
