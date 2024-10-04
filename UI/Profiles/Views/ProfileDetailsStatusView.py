from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import ProfileDetails
################################################################################

__all__ = ("ProfileDetailsStatusView",)

################################################################################
class ProfileDetailsStatusView(FroggeView):

    def __init__(self, owner: User, details: ProfileDetails):
        
        super().__init__(owner, details)
        
        button_list = [
            CharacterNameButton(),
            CustomURLButton(),
            AccentColorButton(),
            RPJobsButton(),
            RatesButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class CharacterNameButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.secondary,
            label="Character Name",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.name)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_name(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class CustomURLButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.secondary,
            label="Custom URL",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.custom_url)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_url(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class AccentColorButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.secondary,
            label="Accent Color",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.color)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_color(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RPJobsButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.secondary,
            label="RP Jobs",
            disabled=False,
            row=1
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.jobs)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_jobs(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RatesButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.secondary,
            label="Rates",
            disabled=False,
            row=1
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.rates)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_rates(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
