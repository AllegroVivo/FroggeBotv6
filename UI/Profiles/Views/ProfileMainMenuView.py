from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from Assets import BotEmojis
from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import Profile
################################################################################

__all__ = ("ProfileMainMenuView",)

################################################################################
class ProfileMainMenuView(FroggeView):

    def __init__(self, owner: User, profile: Profile):
        
        super().__init__(owner, profile)
        
        button_list = [
            MainDetailsButton(),
            AtAGlanceButton(),
            PersonalityButton(),
            ImagesButton(),
            PostProfileButton(),
            ProfileProgressButton(),
            PreviewProfileButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class MainDetailsButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Main Info & Details",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.main_details_menu(interaction)
        
################################################################################
class AtAGlanceButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="At A Glance Section",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.ataglance_menu(interaction)
        
################################################################################
class PersonalityButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Personality Elements",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.personality_menu(interaction)
        
################################################################################
class ImagesButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Add/Remove Images",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.images_menu(interaction)
        
################################################################################
class PreviewProfileButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.secondary,
            label="Preview Profile",
            disabled=False,
            row=1,
            emoji=BotEmojis.EmojiMonocle
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.preview_profile(interaction)
        
################################################################################
class PostProfileButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.secondary,
            label="Post/Update Profile",
            disabled=False,
            row=1,
            emoji=BotEmojis.FlyingEnvelope
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.post(interaction)
        
################################################################################
class ProfileProgressButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.secondary,
            label="Profile Progress",
            disabled=False,
            row=1,
            emoji=BotEmojis.Goose
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.progress(interaction)
        
################################################################################
