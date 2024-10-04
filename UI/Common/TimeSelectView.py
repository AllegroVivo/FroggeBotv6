from __future__ import annotations

from typing import List

from discord import User, Interaction, SelectOption
from discord.ui import Select

from Enums import Hours, Minutes
from UI.Common import FroggeView, CloseMessageButton
################################################################################

__all__ = ("TimeSelectView",)

################################################################################
class TimeSelectView(FroggeView):

    def __init__(self, owner: User, hours: List[SelectOption], minutes: List[SelectOption]):
        
        super().__init__(owner, None)
        
        self.hour = None
        
        button_list = [
            HourSelect(hours, minutes),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class HourSelect(Select):
    
    def __init__(self, hours: List[SelectOption], minutes: List[SelectOption]):
        
        super().__init__(
            placeholder="Select an hour...",
            options=hours,
            min_values=1,
            max_values=1,
            disabled=False,
            row=0,
        )
        
        self.minutes = minutes
        
    async def callback(self, interaction: Interaction):
        self.view.hour = Hours(int(self.values[0]))

        self.view.add_item(MinuteSelect(self.minutes)) 
        self.placeholder = self.view.hour.proper_name
        self.disabled = True
        
        await interaction.edit(view=self.view)
        
################################################################################
class MinuteSelect(Select):
    
    def __init__(self, minutes: List[SelectOption]):
        
        super().__init__(
            placeholder="Select a minute increment...",
            options=minutes,
            min_values=1,
            max_values=1,
            disabled=False,
            row=1,
        )
        
    async def callback(self, interaction: Interaction):
        self.view.value = self.view.hour, Minutes(int(self.values[0]))
        self.view.complete = True
        
        await self.view.dummy_response(interaction)
        await self.view.stop()  # type: ignore
        
################################################################################
