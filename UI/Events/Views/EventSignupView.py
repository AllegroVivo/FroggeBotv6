from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ButtonStyle, Interaction
from discord.ui import Button, View
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import StaffableEvent, EventPosition
################################################################################

__all__ = ("EventSignupView",)

################################################################################
class EventSignupView(View):

    def __init__(self, event: StaffableEvent):
        
        super().__init__(timeout=None)
        
        self.event: StaffableEvent = event
        
        button_list = [EventPositionSignupButton(p) for p in self.event.positions]
        for btn in button_list:
            self.add_item(btn)
        self.add_item(AdministratorConsoleButton(self.event.id))
        
################################################################################
class EventPositionSignupButton(Button):
    
    def __init__(self, event_pos: EventPosition):
        
        super().__init__(
            style=ButtonStyle.primary,
            label=event_pos.position.name,
            disabled=False,
            emoji=event_pos.emoji,
            custom_id=f"event_pos_signup_{event_pos.id}"
        )
        
        self.position: EventPosition = event_pos
        self.set_disabled()
        
    def set_disabled(self) -> None:
        
        self.disabled = self.position.signups == self.position.quantity
        
    async def callback(self, interaction: Interaction):
        await self.position.toggle_user_signup(interaction)
        self.set_disabled()

        try:
            await interaction.message.edit(embeds=await self.view.event.compile(), view=self.view)
        except:
            try:
                await interaction.edit_original_response(embeds=await self.view.event.compile(), view=self.view)
            except Exception as e:
                print(e)
                pass
        
################################################################################
class AdministratorConsoleButton(Button):

    def __init__(self, event_id: int):

        super().__init__(
            style=ButtonStyle.danger,
            label="Admin Console",
            disabled=False,
            emoji="🛠️",
            custom_id=f"{event_id}_admin_console"
        )

    async def callback(self, interaction: Interaction):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You do not have permission to access this console. Nice Try~", ephemeral=True)
            return

        await self.view.event.menu(interaction)

################################################################################
