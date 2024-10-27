from __future__ import annotations

from discord import User, Interaction
from discord.ui import Select

from Enums import DataCenter, GameWorld
from UI.Common import FroggeView, CloseMessageButton
################################################################################

__all__ = ("HomeWorldSelectView",)

################################################################################
class HomeWorldSelectView(FroggeView):

    def __init__(self, owner: User):
        
        super().__init__(owner, None)
        
        component_list = [
            DataCenterSelect(),
            CloseMessageButton()
        ]
        for btn in component_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class DataCenterSelect(Select):
    
    def __init__(self):
        
        super().__init__(
            placeholder="Select a Data Center...",
            options=DataCenter.select_options(),
            max_values=1,
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        self.view.add_item(HomeWorldSelect(DataCenter(int(self.values[0]))))
        
        self.placeholder = DataCenter(int(self.values[0])).proper_name
        self.disabled = True
        
        await self.view.edit_message_helper(interaction, view=self.view)
        
################################################################################
class HomeWorldSelect(Select):
    
    def __init__(self, dc: DataCenter):
        
        super().__init__(
            placeholder="Select your Home World...",
            options=GameWorld.select_options_by_dc(dc),
            max_values=1,
            disabled=False,
            row=1
        )
        
        self.dc: DataCenter = dc
        
    async def callback(self, interaction: Interaction):
        self.view.value = self.dc, GameWorld(int(self.values[0]))
        self.view.complete = True
        
        await self.view.dummy_response(interaction)
        await self.view.stop()  # type: ignore
        
################################################################################
