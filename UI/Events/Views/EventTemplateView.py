from __future__ import annotations

from typing import TYPE_CHECKING
from discord import Interaction, User, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import Event
################################################################################

__all__ = ("EventTemplateView",)

################################################################################
class EventTemplateView(FroggeView):
    
    def __init__(self, event: Event):
        
        super().__init__(None, event)  # type: ignore
        
        self.add_item(MakeEventButton(event))
        self.add_item(CloseMessageButton())
        
################################################################################
class MakeEventButton(FroggeButton):
    
    def __init__(self, event: Event):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Create New Event from this Template",
            disabled=False,
            row=0
        )
        
        self.event_id: int = event.id
        
    async def callback(self, interaction: Interaction):
        event = self.view.ctx[self.event_id]
        if event is None:
            return
        
        await self.view.cancel()

        new_event = event.copy(event)
        await new_event.menu(interaction)

################################################################################
