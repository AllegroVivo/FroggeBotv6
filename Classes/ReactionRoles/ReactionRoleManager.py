from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Union, Dict

from discord import (
    Interaction,
    User,
    Embed,
    EmbedField,
    TextChannel,
    ForumChannel, ChannelType
)

from Classes.Common import ObjectManager, LazyChannel
from Errors import MaxItemsReached
from UI.Common import FroggeSelectView
from UI.ReactionRoles import ReactionRoleManagerMenuView
from Utilities import Utilities as U
from .ReactionRoleMessage import ReactionRoleMessage

if TYPE_CHECKING:
    from Classes import GuildData
    from UI.Common import FroggeView
################################################################################

__all__ = ("ReactionRoleManager",)

################################################################################
class ReactionRoleManager(ObjectManager):

    __slots__ = (
        "_channel",
    )
    
################################################################################
    def __init__(self, state: GuildData) -> None:

        super().__init__(state)

        self._channel: LazyChannel = LazyChannel(self, None)
    
################################################################################
    async def load_all(self, payload: Dict[str, Any]) -> None:
        
        self._managed = [ReactionRoleMessage.load(self, m) for m in payload["messages"]]
        self._channel = LazyChannel(self, payload.get("channel_id"))

        for message in self._managed:
            await message.update_post_components()

################################################################################
    @property
    def messages(self) -> List[ReactionRoleMessage]:

        return self._managed  # type: ignore

################################################################################
    @property
    async def channel(self) -> Optional[Union[TextChannel, ForumChannel]]:

        return await self._channel.get()

    @channel.setter
    def channel(self, value: Optional[Union[TextChannel, ForumChannel]]) -> None:

        self._channel.set(value)

################################################################################
    def update(self) -> None:

        self.bot.api.update_reaction_role_manager(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "channel_id": self._channel.id
        }

################################################################################
    async def status(self) -> Embed:

        channel = await self.channel
        return U.make_embed(
            title="__Reaction Roles Module Status__",
            description=(
                f"**Total Configured Reaction Roles:** [`{len(self.messages)}`]\n"
                f"**Reaction Roles Channel:** {channel.mention if channel else '`Not Set`'}"
            ),
            fields=[
                EmbedField(
                    name="**__Message Listing__**",
                    value=(
                        "\n".join(
                            f"* **{role.title or 'Untitled Message'}**"
                            for role in self.messages
                        )
                    ) if self.messages else "`No Messages Configured`",
                    inline=False
                )
            ]
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:
        
        return ReactionRoleManagerMenuView(user, self)

################################################################################
    async def add_item(self, interaction: Interaction) -> None:

        if len(self.messages) >= self.MAX_ITEMS:
            error = MaxItemsReached("Reaction Roles", self.MAX_ITEMS)
            await interaction.respond(embed=error, ephemeral=True)
            return

        new_role = ReactionRoleMessage.new(self)
        self._managed.append(new_role)  # type: ignore

        await new_role.menu(interaction)

################################################################################
    async def modify_item(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Modify Reaction Role__",
            description=(
                "Please select the reaction role message you would like to modify."
            )
        )
        view = FroggeSelectView(interaction.user, [m.select_option() for m in self.messages])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        role = self[view.value]
        await role.menu(interaction)

################################################################################
    async def remove_item(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Reaction Role__",
            description=(
                "Please select the reaction role message you would like to remove."
            )
        )
        view = FroggeSelectView(interaction.user, [m.select_option() for m in self.messages])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        role = self[view.value]
        await role.remove(interaction)

################################################################################
    async def set_channel(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Reaction Roles Channel__",
            description=(
                "Please mention the channel where you would like to set up the Reaction Roles."
            )
        )

        channel = await U.listen_for(
            interaction=interaction,
            prompt=prompt,
            mentionable_type=U.MentionableType.Channel,
            channel_restrictions=[ChannelType.text]
        )
        if channel is None:
            return

        self.channel = channel

################################################################################
