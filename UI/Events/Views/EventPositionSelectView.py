from __future__ import annotations

from typing import List, TYPE_CHECKING

from discord import User, Interaction, SelectOption
from discord.ui import Select

from UI.Common import CloseMessageButton, FroggeView
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import Event
################################################################################

__all__ = ("EventPositionSelectView",)

################################################################################
class EventPositionSelectView(FroggeView):

    def __init__(self, owner: User, event: Event):
        
        super().__init__(owner, event)

        self.position = None

        raw_options = event.guild.position_manager.select_options()
        options = [
            o
            for o in raw_options
            if o.value not in [p.position.id for p in event.positions]
        ]

        self.add_item(PositionSelect(options))
        self.add_item(CloseMessageButton())
        
################################################################################
class PositionSelect(Select):
    
    def __init__(self, options: List[SelectOption]):

        if not options:
            options.append(SelectOption(label="No positions available", value="-1"))
        
        super().__init__(
            placeholder="Select a position...",
            options=options,
            disabled=options[0].value == "-1",
            row=0,
            max_values=len(options),
        )
        
    async def callback(self, interaction: Interaction):
        self.view.value = [int(i) for i in self.values]

        selected = [o for o in self.options if o.value in self.values]
        self.placeholder = U.string_clamp(", ".join([o.label for o in selected]), 70)
        self.disabled = True

        self.view.add_item(QuantitySelect())

        await interaction.response.edit_message()
        await self.view.edit_message_helper(interaction=interaction, view=self.view)

################################################################################
class QuantitySelect(Select):

    def __init__(self):

        super().__init__(
            placeholder="Select a quantity...",
            options=[SelectOption(label=str(i), value=str(i)) for i in range(1, 10)],
            disabled=False,
            row=1,
        )

    async def callback(self, interaction: Interaction):
        self.view.value = (self.view.value, int(self.values[0]))
        self.view.complete = True

        await interaction.response.edit_message()
        await self.view.stop()  # type: ignore

################################################################################
