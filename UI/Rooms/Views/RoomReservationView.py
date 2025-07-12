from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Interaction, PartialEmoji, ButtonStyle
from discord.ui import View

from Assets import BotEmojis
from UI.Common import FroggeButton

if TYPE_CHECKING:
    from Classes import Room
################################################################################

__all__ = ("RoomReservationView",)

################################################################################
class RoomReservationView(View):

    def __init__(self, room: Room):
        
        super().__init__(timeout=None)
        
        self.room: Room = room

        if not room._occupant:
            if not self.room.disabled:
                self.add_item(ReserveRoomButton(room))
                if self.room.locked:
                    self.add_item(NotifyOwnerButton(room))
        else:
            self.add_item(ReleaseRoomButton(room))

################################################################################
class ReserveRoomButton(FroggeButton):
    
    def __init__(self, room: Room):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Reserve Room",
            disabled=room._in_use,
            row=0,
            emoji=BotEmojis.Star,
            custom_id=f"reserve_room-{room.id}"
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.room.reserve(interaction)
        
################################################################################
class NotifyOwnerButton(FroggeButton):

    def __init__(self, room: Room):

        super().__init__(
            style=ButtonStyle.primary,
            label="Request Unlock",
            disabled=room._in_use or room._details._owner.id is None,
            row=0,
            emoji=BotEmojis.Lock,
            custom_id=f"unlock-{room.id}"
        )

    async def callback(self, interaction: Interaction):
        await self.view.room.notify_owner(interaction)

################################################################################
class ReleaseRoomButton(FroggeButton):

    def __init__(self, room: Room):

        super().__init__(
            style=ButtonStyle.primary,
            label="Release Reservation",
            disabled=False,
            row=0,
            emoji=BotEmojis.Unlock,
            custom_id=f"release-{room.id}"
        )

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.view.room._occupant.id:
            await interaction.response.send_message(
                "You cannot release this room as you are not the occupant.",
                ephemeral=True
            )
            return
        await self.view.room.release()
        await interaction.edit()

################################################################################
