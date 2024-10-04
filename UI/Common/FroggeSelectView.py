from __future__ import annotations

from typing import List

from discord import User, Interaction, SelectOption
from discord.ui import Select

from .FroggeView import FroggeView
from .CloseMessageButton import CloseMessageButton
################################################################################

__all__ = ("FroggeSelectView",)

################################################################################
class FroggeSelectView(FroggeView):

    def __init__(
        self, 
        owner: User, 
        options: List[SelectOption], 
        multi_select: bool = False,
        return_interaction: bool = False
    ):
        
        super().__init__(owner, None)
        
        self.return_interaction = return_interaction
        
        button_list = [
            OptionSelect(options, multi_select),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class OptionSelect(Select):
    
    def __init__(self, options: List[SelectOption], multi_select: bool):
        
        if not options:
            options.append(SelectOption(label="No options available", value="-1"))
        
        super().__init__(
            placeholder="Select an option...",
            options=options,
            min_values=1,
            max_values=1 if not multi_select else len(options),
            disabled=options[0].value == "-1",
            row=0,
        )
        
        self.multi_select = multi_select
        
    async def callback(self, interaction: Interaction):
        if not self.view.return_interaction:
            self.view.value = self.values if self.multi_select else self.values[0]
        else:
            self.view.value = (
                self.values if self.multi_select else self.values[0],
                interaction
            )
        self.view.complete = True
        
        if not self.view.return_interaction:
            await interaction.message.edit()
        await self.view.stop()  # type: ignore
        
################################################################################
