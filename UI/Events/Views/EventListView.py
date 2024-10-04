from __future__ import annotations

from typing import TYPE_CHECKING
from discord import Interaction, User, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import StaffableEvent
################################################################################

__all__ = ("EventListView",)

################################################################################
class EventListView(FroggeView):
    
    def __init__(self, event: StaffableEvent):
        
        super().__init__(None, event)  # type: ignore
        
        self.add_item(EditEventButton(event))
        self.add_item(CloseMessageButton())
        
################################################################################
class EditEventButton(FroggeButton):
    
    def __init__(self, event: StaffableEvent):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Edit this Event",
            disabled=False,
            row=0
        )
        
        self.event_id: str = event.id
        
    async def callback(self, interaction: Interaction):
        event = self.view.ctx[self.event_id]
        if event is None:
            return
        
        await self.view.cancel()
        await event.menu(interaction)

################################################################################
