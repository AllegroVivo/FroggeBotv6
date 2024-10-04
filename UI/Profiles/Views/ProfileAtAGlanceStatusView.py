from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import ProfileAtAGlance
################################################################################

__all__ = ("ProfileAtAGlanceStatusView",)

################################################################################
class ProfileAtAGlanceStatusView(FroggeView):

    def __init__(self, owner: User, aag: ProfileAtAGlance):
        
        super().__init__(owner, aag)
        
        button_list = [
            RaceClanButton(),
            GenderPronounsButton(),
            OrientationButton(),
            HeightButton(),
            AgeButton(),
            MareButton(),
            HomeWorldButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class HomeWorldButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Home World",
            disabled=False,
            row=1
        )
        
    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.world)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_world(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class GenderPronounsButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Gender/Pronouns",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.gender)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_gender(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RaceClanButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Race/Clan",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.race)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_raceclan(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class OrientationButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Orientation",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.orientation)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_orientation(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class HeightButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Height",
            disabled=False,
            row=1
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.height)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_height(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class AgeButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Age",
            disabled=False,
            row=1
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.age)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_age(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class MareButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Mare ID",
            disabled=False,
            row=1
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.mare)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_mare(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
