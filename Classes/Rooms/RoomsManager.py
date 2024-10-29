from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Dict, Union

from discord import Interaction, User, Embed, EmbedField, TextChannel, ForumChannel

from Classes.Common import ObjectManager, LazyChannel
from Utilities import Utilities as U
from .Room import Room
from Errors import MaxItemsReached, ChannelNotSet
from UI.Rooms import RoomsManagerMenuView
from UI.Common import FroggeMultiMenuSelect

if TYPE_CHECKING:
    from Classes import GuildData
    from UI.Common import FroggeView
################################################################################

__all__ = ("RoomsManager", )

################################################################################
class RoomsManager(ObjectManager):

    __slots__ = (
        "_channel",
    )

    MAX_ITEMS = 80  # (4x Select Menus @ 20 items each)

################################################################################
    def __init__(self, state: GuildData) -> None:

        super().__init__(state)

        self._channel: LazyChannel = LazyChannel(self, None)

################################################################################
    async def load_all(self, payload: Dict[str, Any]) -> None:

        self._managed = [Room.load(self, r) for r in payload["rooms"]]
        self._channel = LazyChannel(self, payload["channel_id"])

        for room in self.rooms:
            await room.update_post_components()

################################################################################
    @property
    def rooms(self) -> List[Room]:

        self._managed.sort(key=lambda r: r.index)
        return self._managed  # type: ignore

################################################################################
    @property
    async def channel(self) -> Union[TextChannel, ForumChannel]:

        return await self._channel.get()

    @channel.setter
    def channel(self, value: Union[TextChannel, ForumChannel]) -> None:

        self._channel.set(value)

################################################################################
    def update(self) -> None:

        self.bot.api.update_room_manager(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "channel_id": self._channel.id,
        }

################################################################################
    async def status(self) -> Embed:

        fields = [r.field() for r in self.rooms]
        if not fields:
            fields.append(EmbedField(
                name="`No Rooms Configured`",
                value="** **",
                inline=False
            ))

        desc = "Below is a summary of your venue's configured rooms."
        channel = await self.channel
        return U.make_embed(
            title="__Rooms Module Status__",
            description=(
                f"**Rooms Channel:**\n"
                f"{channel.mention if channel else '`Not Set`'}\n\n"
                
                f"{desc}\n"
                f"{U.draw_line(text=desc)}"
            ),
            fields=fields
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return RoomsManagerMenuView(user, self)

################################################################################
    def _get_next_index(self):

        # Extract and sort indices, ensuring they are integers
        indices = sorted([int(room.index) for room in self.rooms if room.index is not None])

        # If there are no rooms, return the first index (assuming starting at 0 or 1)
        if not indices:
            return 1

        # Check for the first missing index
        for i in range(1, max(indices) + 1):
            if i not in indices:
                return i

        # If no index is missing, return the next available index (max + 1)
        return max(indices) + 1

################################################################################
    async def add_item(self, interaction: Interaction) -> None:

        if len(self) >= self.MAX_ITEMS:
            error = MaxItemsReached("Rooms", self.MAX_ITEMS)
            await interaction.respond(embed=error, ephemeral=True)
            return

        new_room = Room.new(self, self._get_next_index())
        self._managed.append(new_room)

        await new_room.menu(interaction)

################################################################################
    async def modify_item(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Select Room to Modify__",
            description=(
                "Please select the room you would like to modify."
            )
        )
        view = FroggeMultiMenuSelect(
            interaction.user, None, [r.select_option() for r in self.rooms]
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        room = self[view.value]
        await room.menu(interaction)

################################################################################
    async def remove_item(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Select Room to Remove__",
            description=(
                "Please select the room you would like to remove."
            )
        )
        view = FroggeMultiMenuSelect(
            interaction.user, None, [r.select_option() for r in self.rooms]
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        room = self[view.value]
        await room.remove(interaction)

################################################################################
    async def set_channel(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Rooms Channel__",
            description=(
                "Please select the channel you would like to use for the Rooms module."
            )
        )
        channel = await U.select_channel(interaction, self.guild, "Rooms Channel", prompt)
        if channel is None:
            return

        self.channel = channel

################################################################################
    async def post_all(self, interaction: Interaction) -> None:

        post_channel = await self.channel
        if post_channel is None:
            error = ChannelNotSet("Room Check")
            await interaction.respond(embed=error, ephemeral=True)
            return

        await interaction.response.defer(invisible=False)

        for room in self.rooms:
            await room.post(interaction)

        confirm = U.make_embed(
            title="__Rooms Posted__",
            description=(
                f"All rooms have been posted to {post_channel.mention}."
            )
        )
        await interaction.followup.send(embed=confirm)

################################################################################
    async def check_end_times(self) -> None:

        for room in self.rooms:
            await room.check_end_time()

################################################################################
