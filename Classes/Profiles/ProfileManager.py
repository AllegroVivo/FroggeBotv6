from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Dict, Union, Optional

from discord import Interaction, User, Embed, TextChannel, ForumChannel, Role, EmbedField

from Classes.Common import ObjectManager
from .Profile import Profile
from .ProfileRequirements import ProfileRequirements
from .ProfileChannelGroup import ProfileChannelGroup
from Utilities import Utilities as U
from Errors import MaxItemsReached
from UI.Profiles import ProfileManagerMenuView, ProfileChannelsMenuView
from UI.Common import FroggeSelectView

if TYPE_CHECKING:
    from Classes import GuildData
    from UI.Common import FroggeView
################################################################################

__all__ = ("ProfileManager", )

################################################################################
class ProfileManager(ObjectManager):

    __slots__ = (
        "_requirements",
        "_channels"
    )

    MAX_CHANNEL_GROUPS = 8  # (Three fields per line in the embed) 
    
################################################################################
    def __init__(self, state: GuildData) -> None:

        super().__init__(state)
        
        self._requirements: ProfileRequirements = ProfileRequirements(self)
        self._channels: List[ProfileChannelGroup] = []
    
################################################################################
    async def load_all(self, payload: Dict[str, Any]) -> None:
        
        self._requirements.load(payload["requirements"])
        self._channels = [
            ProfileChannelGroup.load(self, data)
            for data in payload["channel_groups"]
        ]
        self._managed = [Profile.load(self, data) for data in payload["profiles"]]

################################################################################
    @property
    def profiles(self) -> List[Profile]:
        
        return self._managed
    
################################################################################
    @property
    def requirements(self) -> ProfileRequirements:
        
        return self._requirements
   
################################################################################
    @property
    def channel_groups(self) -> List[ProfileChannelGroup]:
        
        return self._channels
    
################################################################################
    def get_profile_by_user(self, user_id: int) -> Optional[Profile]:

        return next((p for p in self.profiles if p._user.id == int(user_id)), None)

################################################################################
    async def allowed_roles(self) -> List[Role]:

        ret = []
        for group in self._channels:
            ret.extend(await group.roles)
            
        return ret

################################################################################
    async def status(self) -> Embed:

        posted_profiles = [p for p in self.profiles if p._post_msg.id is not None]

        posted_names = [p.name for p in posted_profiles]
        name_str1 = name_str2 = ""

        if len(posted_names) > 0:
            for i, name in enumerate(posted_names):
                if i % 2 == 0:
                    name_str1 += f"* `{name}`\n"
                else:
                    name_str2 += f"* `{name}`\n"

        if not name_str1:
            name_str1 = "`None Posted`"
            name_str2 = "** **"

        return U.make_embed(
            title="__Profile System Management__",
            description=f"**[`{len(self._requirements)}/17`]** Requirements Active",
            fields=[
                EmbedField(
                    name="__Posted Profiles__",
                    value=name_str1,
                    inline=True,
                ),
                EmbedField(
                    name="** **",
                    value=name_str2,
                    inline=True,
                ),
            ],
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:
        
        return ProfileManagerMenuView(user, self)

################################################################################
    async def add_item(self, interaction: Interaction) -> None:
        
        pass

################################################################################
    async def modify_item(self, interaction: Interaction) -> None:
        
        pass

################################################################################
    async def remove_item(self, interaction: Interaction) -> None:
        
        pass
    
################################################################################
    async def post_channels_for(self, user: User) -> List[Union[TextChannel, ForumChannel]]:

        member = await self.guild.get_or_fetch_member(user.id)
        if member is None:
            return []

        ret = []
        for group in self._channels:
            if any(r in member.roles for r in await group.roles):
                ret.extend(await group.channels)

        return ret

################################################################################
    async def allowed_to_post(self, user: User) -> bool:

        member = await self.guild.get_or_fetch_member(user.id)
        if member is None:
            return False

        allowed_roles = await self.allowed_roles()
        return any(r in member.roles for r in allowed_roles)

################################################################################
    def _new_profile(self, user_id: int) -> Profile:

        new_profile = Profile.new(self, user_id)
        self._managed.append(new_profile)
        return new_profile

################################################################################
    async def user_main_menu(self, interaction: Interaction) -> None:

        staff = self.guild.staff_manager[interaction.user.id]
        if staff is None:
            error = U.make_error(
                title="User Not Registered",
                message=f"{interaction.user.mention} is not registered as a staff member.",
                solution="Please hire this user before proceeding."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        await staff.profile_main_menu(interaction)

################################################################################
    async def requirements_menu(self, interaction: Interaction) -> None:

        await self._requirements.menu(interaction)

################################################################################
    async def channel_status(self) -> Embed:

        fields = []
        for i, group in enumerate(self._channels):
            channel_str = "\n".join([f"* {c.mention}" for c in await group.channels])
            role_str = "\n".join([f"* {r.mention}" for r in await group.roles])

            fields.append(
                EmbedField(
                    name=f"__Channel Group {i + 1}__",
                    value=(
                        f"__Channels__\n"
                        f"{channel_str}"
                    ),
                    inline=True
                )
            )
            fields.append(
                EmbedField(
                    name="** **",
                    value=(
                        f"__Roles__\n"
                        f"{role_str}"
                    ),
                    inline=True
                )
            )
            fields.append(EmbedField("** **", "** **", True))

        if not fields:
            fields.append(
                EmbedField(
                    name="__Channel Groups__",
                    value="`No Posting Channels Defined`",
                    inline=False
                )
            )

        return U.make_embed(
            title="__Profile Channel Associations__",
            fields=fields,
        )

################################################################################
    async def channels_menu(self, interaction: Interaction) -> None:

        embed = await self.channel_status()
        view = ProfileChannelsMenuView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def add_channel_group(self, interaction: Interaction) -> None:

        if len(self._channels) >= self.MAX_CHANNEL_GROUPS:
            error = MaxItemsReached("Channel Groups", self.MAX_CHANNEL_GROUPS)
            await interaction.respond(embed=error, ephemeral=True)
            return

        new_group = ProfileChannelGroup.new(self)
        self._channels.append(new_group)

        await new_group.menu(interaction)

################################################################################
    async def modify_channel_group(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Modify Channel Group__",
            description="Please select the channel group you would like to modify."
        )
        view = FroggeSelectView(
            owner=interaction.user,
            options=[await g.select_option() for g in self._channels]
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        group = next((g for g in self._channels if g.id == int(view.value)), None)
        if group is None:
            return

        await group.menu(interaction)

################################################################################
    async def remove_channel_group(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Channel Group__",
            description="Please select the channel group you would like to remove."
        )
        view = FroggeSelectView(
            owner=interaction.user,
            options=[await g.select_option() for g in self._channels]
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        group = next((g for g in self._channels if g.id == int(view.value)), None)
        if group is None:
            return

        await group.remove(interaction)

################################################################################
