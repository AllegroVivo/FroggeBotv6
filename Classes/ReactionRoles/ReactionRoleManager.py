from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Optional, Union, Dict

from discord import (
    Interaction,
    User,
    Embed,
    EmbedField,
    TextChannel,
    ForumChannel, ChannelType, SelectOption
)

from Classes.Common import ObjectManager, LazyChannel
from Errors import MaxItemsReached
from UI.Common import FroggeSelectView, ConfirmCancelView
from UI.ReactionRoles import ReactionRoleManagerMenuView
from Utilities import Utilities as U, FroggeColor
from .ReactionRoleMessage import ReactionRoleMessage
from .ReactionRoleTemplate import ReactionRoleTemplate

if TYPE_CHECKING:
    from Classes import GuildData
    from UI.Common import FroggeView
################################################################################

__all__ = ("ReactionRoleManager",)

################################################################################
class ReactionRoleManager(ObjectManager):

    __slots__ = (
        "_channel",
        "_templates",
    )
    
################################################################################
    def __init__(self, state: GuildData) -> None:

        super().__init__(state)

        self._channel: LazyChannel = LazyChannel(self, None)
        self._templates: List[ReactionRoleTemplate] = []

        for json_file in Path(f"Classes/ReactionRoles/Templates").glob('*.json'):
            with json_file.open('r', encoding='utf-8') as file:
                self._templates.append(ReactionRoleTemplate(json.load(file)))
    
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

        options = [
            SelectOption(label="Blank Message", value="blank"),
            SelectOption(label="Templated Message", value="template")
        ]
        prompt = U.make_embed(
            title="__Add Reaction Role__",
            description=(
                "Would you like to add a blank reaction role message or create "
                "one from a template of pre-existing options?"
            )
        )
        view = FroggeSelectView(interaction.user, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        if view.value == "template":
            await self._create_new_role_from_template(interaction)
            return

        new_role = ReactionRoleMessage.new(self)
        self._managed.append(new_role)  # type: ignore

        await new_role.menu(interaction)
        return

################################################################################
    async def _create_new_role_from_template(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Create Reaction Role from Template__",
            description=(
                "Please select the template you would like to use for the new reaction roles."
            )
        )
        view = FroggeSelectView(interaction.user, [t.select_option() for t in self._templates])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        template = next(t for t in self._templates if t.name == view.value)

        confirm = U.make_embed(
            title=f"__Create `{template.name}` Reaction Roles__",
            description=(
                f"Would you like to create a new reaction role message using "
                f"the `{template.name}` template?"
            )
        )
        view = ConfirmCancelView(interaction.user, return_interaction=True)

        await interaction.respond(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        _, inter = view.value
        await inter.response.defer(invisible=False)

        new_roles = []
        for template_role in template.roles:
            new_roles.append(
                await self.guild.parent.create_role(
                    name=template_role.name,
                    color=FroggeColor(int(template_role.color.lstrip("#"), 16))
                )
            )

        new_reaction_role = ReactionRoleMessage.new(self)
        self._managed.append(new_reaction_role)  # type: ignore

        new_reaction_role._title = template.title
        new_reaction_role._description = template.description
        new_reaction_role._thumbnail = template.thumbnail
        new_reaction_role._type_param = template.type.value
        new_reaction_role.update()

        for role in new_roles:
            new_reaction_role.add_role_from_role(role, template)

        await inter.followup.send("** **", delete_after=0.1)
        await new_reaction_role.menu(interaction)

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
                "Please select the channel where you would like to set up the "
                "Reaction Roles."
            )
        )

        channel = await U.select_channel(
            interaction=interaction,
            guild=self.guild,
            channel_type="Reaction Roles Channel",
            channel_prompt=prompt
        )
        if channel is None:
            return

        self.channel = channel

################################################################################
