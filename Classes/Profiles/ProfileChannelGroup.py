from __future__ import annotations

from typing import TYPE_CHECKING, List, Union, Type, TypeVar, Any, Tuple, Dict

from discord import (
    TextChannel,
    Role,
    Interaction,
    ForumChannel,
    Embed,
    EmbedField,
    SelectOption,
    ChannelType, User,
)

from Assets import BotEmojis
from Errors import MaxItemsReached
from Utilities import Utilities as U
from UI.Common import ConfirmCancelView, FroggeSelectView, FroggeView
from UI.Profiles import ProfileChannelGroupStatusView
from Classes.Common import ManagedObject, LazyChannel, LazyRole

if TYPE_CHECKING:
    from Classes import ProfileManager
################################################################################

__all__ = ("ProfileChannelGroup",)

PCG = TypeVar("PCG", bound="ProfileChannelGroup")

################################################################################
class ProfileChannelGroup(ManagedObject):

    __slots__ = (
        "_channels",
        "_roles",
    )
    
    MAX_ITEMS = 10
    
################################################################################
    def __init__(self, mgr: ProfileManager, _id: int, **kwargs) -> None:

        super().__init__(mgr, _id)
        
        self._channels: List[LazyChannel] = [LazyChannel(self, c) for c in kwargs.get("channel_ids", [])]
        self._roles: List[LazyRole] = [LazyRole(self, r) for r in kwargs.get("role_ids", [])]
    
################################################################################
    @classmethod
    def new(cls: Type[PCG], mgr: ProfileManager) -> PCG:
        
        new_data = mgr.bot.api.create_profile_channel_group(mgr.guild_id)
        return cls(mgr, new_data["id"])
    
################################################################################
    @classmethod
    def load(cls: Type[PCG], mgr: ProfileManager, data: Dict[str, Any]) -> PCG:
        
        self: PCG = cls.__new__(cls)
        
        self._id = data["id"]
        self._mgr = mgr
        
        self._channels = [LazyChannel(self, c) for c in data["channel_ids"]]
        self._roles = [LazyRole(self, r) for r in data["role_ids"]]
        
        return self
    
################################################################################
    @property
    async def channels(self) -> List[Union[TextChannel, ForumChannel]]:
        
        return [await c.get() for c in self._channels]
    
################################################################################
    @property
    async def roles(self) -> List[Role]:
        
        return [await r.get() for r in self._roles]
    
################################################################################
    def update(self) -> None:
        
        self.bot.api.update_profile_channel_group(self)
        
################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "channel_ids": [c.id for c in self._channels],
            "role_ids": [r.id for r in self._roles]
        }

################################################################################
    def delete(self) -> None:
        
        self.bot.api.delete_profile_channel_group(self)
        self._mgr._channels.remove(self)  # type: ignore
        
################################################################################
    async def status(self) -> Embed:
        
        channel_str = "\n".join([f"* {c.mention}" for c in await self.channels])
        role_str = "\n".join([f"* {r.mention}" for r in await self.roles])
        
        return U.make_embed(
            title="__Profile Channel Group Status__",
            description=(
                "__**What's This?**__\n"
                "*The following list of channels may\n"
                "be used to post profiles by users\n"
                "with the given linked roles.*"
            ),
            fields=[
                EmbedField(
                    name="__Channels__",
                    value=channel_str or "`No Channels Defined`",
                    inline=True
                ),
                EmbedField(
                    name="__Roles__",
                    value=role_str or "`No Roles Linked`",
                    inline=True
                )
            ]
        )
    
################################################################################
    def get_menu_view(self, user: User) -> FroggeView:
        
        return ProfileChannelGroupStatusView(user, self)
    
################################################################################
    async def select_option(self) -> SelectOption:
        
        ch_str = ", ".join([c.name for c in await self.channels])
        if not ch_str:
            ch_str = "No Channels Defined"
        return SelectOption(
            label=U.string_clamp(ch_str, 95),
            value=str(self.id)
        )
    
################################################################################
    async def remove(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Remove Channel Group__",
            description=(
                "Are you sure you want to remove this profile posting channel group?\n"
                "This action cannot be undone."
            )
        )
        view = ConfirmCancelView(interaction.user)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.delete()
        
################################################################################
    async def add_channel(self, interaction: Interaction) -> None:
        
        if len(self._channels) >= self.MAX_ITEMS:
            error = MaxItemsReached("Posting Channels", self.MAX_ITEMS)
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        prompt = U.make_embed(
            title="__Add Posting Channel__",
            description=(
                "Please mention the channel you would like to add to this "
                "posting channel group."
            )
        )
        channel = await U.listen_for(
            interaction=interaction, 
            prompt=prompt, 
            mentionable_type=U.MentionableType.Channel,
            channel_restrictions=[ChannelType.text, ChannelType.forum]
        )
        if channel is None:
            return

        current_channels = await self.channels
        if channel in current_channels:
            return
        
        self._channels.append(LazyChannel(self, channel.id))
        self.update()
        
################################################################################
    async def add_role(self, interaction: Interaction) -> None:
        
        if len(self._roles) >= self.MAX_ITEMS:
            error = MaxItemsReached("Linked Roles", self.MAX_ITEMS)
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        prompt = U.make_embed(
            title="__Add Linked Role__",
            description=(
                "Please mention the role you would like to link to this "
                "posting channel group."
            )
        )
        role = await U.listen_for(
            interaction=interaction, 
            prompt=prompt, 
            mentionable_type=U.MentionableType.Role
        )
        if role is None:
            return
        
        self._roles.append(LazyRole(self, role.id))
        self.update()
        
################################################################################
    async def remove_channel(self, interaction: Interaction) -> None:
        
        options = [
            SelectOption(
                label=c.name,
                value=str(c.id)
            ) for c in await self.channels
        ]
        
        prompt = U.make_embed(
            title="__Remove Posting Channel(s)__",
            description=(
                "Please select the channel(s) you would like to remove from this "
                "posting channel group."
            )
        )
        view = FroggeSelectView(interaction.user, options, multi_select=True)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        channel_ids_to_remove = [int(i) for i in view.value]
        for channel in self._channels:
            if channel.id in channel_ids_to_remove:
                self._channels.remove(channel)
                
        self.update()
        
################################################################################
    async def remove_role(self, interaction: Interaction) -> None:
        
        options = [
            SelectOption(
                label=r.name,
                value=str(r.id)
            ) for r in await self.roles
        ]
        
        prompt = U.make_embed(
            title="__Remove Linked Role(s)__",
            description=(
                "Please select the role(s) you would like to remove from this "
                "posting channel group."
            )
        )
        view = FroggeSelectView(interaction.user, options, multi_select=True)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        role_ids_to_remove = [int(i) for i in view.value]
        for role in self._roles:
            if role.id in role_ids_to_remove:
                self._roles.remove(role)
                
        self.update()
        
################################################################################
