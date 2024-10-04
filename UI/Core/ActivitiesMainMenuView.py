from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import User, Interaction, TextChannel, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import ActivitiesManager
################################################################################

__all__ = ("ActivitiesMainMenuView",)

################################################################################
class ActivitiesMainMenuView(FroggeView):

    def __init__(self, owner: User, mgr: ActivitiesManager):
        
        super().__init__(owner, mgr)
        
        button_list = [
            GiveawaysMenuButton(),
            RafflesMenuButton(),
            # ContestsMenuButton(),
            # TournamentsMenuButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class GiveawaysMenuButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Giveaways Menu",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        self.view.complete = True
        await self.view.stop()  # type: ignore
        
        await self.view.ctx.giveaway_manager.main_menu(interaction)
        
################################################################################
class RafflesMenuButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Raffles Menu",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        self.view.complete = True
        await self.view.stop()  # type: ignore
    
        await self.view.ctx.raffle_manager.main_menu(interaction)
            
################################################################################
class TournamentsMenuButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Tournaments Menu",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        self.view.complete = True
        await self.view.stop()  # type: ignore
    
        await self.view.ctx.tournament_manager.main_menu(interaction)
            
################################################################################
class ContestsMenuButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Contests Menu",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        self.view.complete = True
        await self.view.stop()  # type: ignore
    
        await self.view.ctx.contest_manager.main_menu(interaction)
            
################################################################################
