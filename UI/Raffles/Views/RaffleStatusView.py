from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from Assets import BotEmojis
from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import Raffle
################################################################################

__all__ = ("RaffleStatusView",)

################################################################################
class RaffleStatusView(FroggeView):

    def __init__(self, owner: User, raffle: Raffle):
        
        super().__init__(owner, raffle)
        
        button_list = [
            SetNameButton(),
            SetNumWinnersButton(),
            SetWinnerPctButton(),
            SetCostButton(),
            ToggleAutoNotifyButton(),
            ToggleActiveButton(),
            RollWinnersButton(),
            CurrentEntriesReportButton(),
            CloseMessageButton(),
            PostMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class SetNameButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Name",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_name(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetCostButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Cost",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_cost(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetWinnerPctButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Winner Pct.",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_prize(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetNumWinnersButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Num. Winners",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_num_winners(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ToggleAutoNotifyButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            disabled=False,
            row=1
        )
        
    def set_attributes(self) -> None:
        self.style = (
            ButtonStyle.success
            if self.view.ctx.auto_notify
            else ButtonStyle.danger
        )
        self.label = (
            "Auto-Notify: On"
            if self.view.ctx.auto_notify
            else "Auto-Notify: Off"
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.toggle_auto_notify(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ToggleActiveButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            disabled=False,
            row=1
        )
        
    def set_attributes(self) -> None:
        self.style = (
            ButtonStyle.success
            if self.view.ctx._active
            else ButtonStyle.secondary
        )
        self.label = (
            "Currently Active"
            if self.view.ctx._active
            else "Inactive"
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.toggle_active(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RollWinnersButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Roll Winners",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.determine_winners(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class CurrentEntriesReportButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Entries Report",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.entries_report(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class PostMessageButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.secondary,
            label="Post Tracking Message",
            disabled=False,
            row=4,
            emoji=BotEmojis.Star
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.post_tracker(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
