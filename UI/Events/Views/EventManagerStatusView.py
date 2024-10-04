from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import EventManager
################################################################################

__all__ = ("EventManagerStatusView",)

################################################################################
class EventManagerStatusView(FroggeView):

    def __init__(self, owner: User, manager: EventManager):
        
        super().__init__(owner, manager)
        
        button_list = [
            AddEventButton(),
            EventsListButton(),
            RemoveEventButton(),
            EventTemplatesButton(),
            SetScheduleLockoutButton(),
            ScheduleChannelButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class AddEventButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Event",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_item(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveEventButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Event by ID",
            row=0
        )

    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.events) == 0
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_item(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class EventsListButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Events List",
            row=0
        )

    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.events) == 0
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.events_list(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class EventTemplatesButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Event Templates",
            row=1
        )

    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.templates) == 0
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.view_event_templates(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetScheduleLockoutButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Schedule Lockout",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_lockout(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ScheduleChannelButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Default Schedule Channel",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_scheduling_channel(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
