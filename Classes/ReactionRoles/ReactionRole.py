from __future__ import annotations

from typing import TYPE_CHECKING, Optional, TypeVar, Type, Any, Dict

from discord import (
    PartialEmoji,
    Role,
    Embed,
    EmbedField,
    Interaction,
    SelectOption,
    NotFound,
    Forbidden,
    Member
)
from requests import delete

from Classes.Common import Identifiable, LazyRole
from Utilities import Utilities as U
from UI.ReactionRoles import ReactionRoleStatusView
from UI.Common import BasicTextModal, ConfirmCancelView
from Enums import ReactionRoleMessageType
from Errors import InsufficientPermissions
if TYPE_CHECKING:
    from Classes import ReactionRoleMessage, GuildData, FroggeBot
################################################################################

__all__ = ("ReactionRole", )

RR = TypeVar("RR", bound="ReactionRole")

################################################################################
class ReactionRole(Identifiable):

    __slots__ = (
        "_parent",
        "_role",
        "_emoji",
        "_label",
    )

################################################################################
    def __init__(self, parent: ReactionRoleMessage, _id: int, **kwargs) -> None:

        super().__init__(_id)

        self._parent: ReactionRoleMessage = parent

        self._label: Optional[str] = kwargs.get("label")
        self._role: LazyRole = LazyRole(self, kwargs.get("role_id"))
        self._emoji: Optional[PartialEmoji] = kwargs.get("emoji")

################################################################################
    @classmethod
    def new(cls: Type[RR], parent: ReactionRoleMessage) -> RR:

        new_data = parent.bot.api.create_reaction_role(parent.id)
        return cls(parent, new_data["id"])

################################################################################
    @classmethod
    def load(cls: Type[RR], parent: ReactionRoleMessage, data: Dict[str, Any]) -> RR:

        self: RR = cls.__new__(cls)

        self._id = data["id"]
        self._parent = parent

        self._label = data["label"]
        self._role = LazyRole(self, data["role_id"])
        self._emoji = PartialEmoji.from_str(data["emoji"]) if data["emoji"] else None

        return self

################################################################################
    @property
    def bot(self) -> FroggeBot:

        return self._parent.bot

################################################################################
    @property
    def guild(self) -> GuildData:

        return self._parent.guild

################################################################################
    @property
    def label(self) -> Optional[str]:

        return self._label

    @label.setter
    def label(self, value: str) -> None:

        self._label = value
        self.update()

################################################################################
    @property
    async def role(self) -> Optional[Role]:

        return await self._role.get()

    @role.setter
    def role(self, value: Role) -> None:

        self._role.set(value)

################################################################################
    @property
    def emoji(self) -> Optional[PartialEmoji]:

        return self._emoji

    @emoji.setter
    def emoji(self, value: PartialEmoji) -> None:

        self._emoji = value
        self.update()

################################################################################
    def update(self) -> None:

        self.bot.api.update_reaction_role(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "label": self.label,
            "role_id": self._role.id,
            "emoji": str(self.emoji) if self.emoji else None
        }

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_reaction_role(self.id)
        self._parent.roles.remove(self)

################################################################################
    async def status(self) -> Embed:

        return U.make_embed(
            title="__Reaction Role Details__",
            fields=[
                EmbedField(
                    name="__Button Label__",
                    value=self.label or "`Not Set`",
                    inline=True
                ),
                EmbedField(
                    name="__Role__",
                    value=(role := await self.role) and role.mention or "`Not Set`",
                    inline=True
                ),
                EmbedField(
                    name="__Emoji__",
                    value=self.emoji and str(self.emoji) or "`Not Set`",
                    inline=True
                ),
            ]
        )

################################################################################
    async def menu(self, interaction: Interaction) -> None:

        embed = await self.status()
        view = ReactionRoleStatusView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def set_label(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Button Label",
            attribute="Label",
            cur_val=self.label,
            max_length=50,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.label = modal.value

################################################################################
    async def set_role(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Role__",
            description="Please mention the role you would like to assign to this button."
        )

        role = await U.listen_for(interaction, prompt, U.MentionableType.Role)
        if role is None:
            return

        self.role = role

        if self.label is None:
            self.label = role.name

################################################################################
    async def set_emoji(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Emoji__",
            description="Please respond with the emoji you would like to use for this button."
        )

        emoji = await U.listen_for(interaction, prompt, U.MentionableType.Emoji)
        if emoji is None:
            return

        self.emoji = emoji

################################################################################
    async def remove_emoji(self, interaction: Interaction) -> None:

        self.emoji = None
        await interaction.respond("** **", delete_after=0.1)

################################################################################
    def select_option(self) -> SelectOption:

        return SelectOption(
            label=self.label or "Unnamed Option",
            value=str(self.id)
        )

################################################################################
    async def remove(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Reaction Role__",
            description="Are you sure you want to remove this reaction role?"
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.delete()

################################################################################
    async def button_callback(self, interaction: Interaction) -> None:

        member = await self.guild.get_or_fetch_member(interaction.user.id)
        assert member is not None

        match self._parent.message_type:
            case ReactionRoleMessageType.Normal:
                await self._normal_role_callback(interaction, member)
            case ReactionRoleMessageType.Unique:
                await self._unique_role_callback(interaction, member)
            case ReactionRoleMessageType.Verify:
                await self._verify_role_callback(interaction, member)
            case ReactionRoleMessageType.Drop:
                await self._drop_role_callback(interaction, member)
            case ReactionRoleMessageType.Reverse:
                await self._reverse_role_callback(interaction, member)
            case ReactionRoleMessageType.Limit:
                await self._limit_role_callback(interaction, member)
            case ReactionRoleMessageType.Binding:
                await self._binding_role_callback(interaction, member)

################################################################################
    async def _normal_role_callback(self, interaction: Interaction, member: Member) -> None:

        await interaction.response.defer(invisible=False, ephemeral=True)

        role = await self.role
        try:
            if role not in member.roles:
                await member.add_roles(role)
                confirm = U.make_embed(
                    title="__Role Added__",
                    description=f"You have been assigned the `{role.name}` role."
                )
            else:
                await member.remove_roles(role)
                confirm = U.make_embed(
                    title="__Role Removed__",
                    description=f"The `{role.name}` role has been removed."
                )
        except NotFound:
            self.role = None
        except Forbidden:
            error = InsufficientPermissions(None, "Manage Roles")
            await interaction.respond(embed=error, ephemeral=True)
            return
        else:
            await interaction.respond(embed=confirm, ephemeral=True)

################################################################################
    async def _unique_role_callback(self, interaction: Interaction, member: Member) -> None:

        await interaction.response.defer(invisible=False, ephemeral=True)

        role = await self.role
        if role in member.roles:
            try:
                await member.remove_roles(role)
            except NotFound:
                self.role = None
            except Forbidden:
                error = InsufficientPermissions(None, "Manage Roles")
                await interaction.respond(embed=error, ephemeral=True)
                return

            confirm = U.make_embed(
                title="__Role Removed__",
                description=f"The `{role.name}` role has been removed."
            )
        else:
            roles_to_remove = [await r.role for r in self._parent.roles if r != self]
            try:
                await member.add_roles(role, reason="Unique Reaction Role")
                await member.remove_roles(*roles_to_remove, reason="Unique Reaction Role")
            except NotFound:
                self.role = None
            except Forbidden:
                error = InsufficientPermissions(None, "Manage Roles")
                await interaction.respond(embed=error, ephemeral=True)
                return

            confirm = U.make_embed(
                title="__Role Added__",
                description=(
                    f"Any previous roles have been removed and you "
                    f"have been assigned the `{role.name}` role."
                )
            )

        await interaction.respond(embed=confirm, ephemeral=True)

################################################################################
    async def _verify_role_callback(self, interaction: Interaction, member: Member) -> None:

        await interaction.response.defer(invisible=False, ephemeral=True)

        role = await self.role
        if role not in member.roles:
            try:
                await member.add_roles(role)
            except NotFound:
                self.role = None
                return
            except Forbidden:
                error = InsufficientPermissions(None, "Manage Roles")
                await interaction.respond(embed=error, ephemeral=True)
                return
            else:
                confirm = U.make_embed(
                    title="__Role Added__",
                    description=(
                        f"You have been assigned the `{role.name}` role.\n\n"
                        
                        "This role is NOT removable. If you wish to remove it, "
                        "please contact an administrator."
                    )
                )
        else:
            confirm = U.make_embed(
                title="__Role Already Added__",
                description=(
                    f"You already have the `{role.name}` role.\n\n"
                    
                    "This role is NOT removable. If you wish to remove it, "
                    "please contact an administrator."
                )
            )

        await interaction.respond(embed=confirm, ephemeral=True)

################################################################################
    async def _drop_role_callback(self, interaction: Interaction, member: Member) -> None:

        await interaction.response.defer(invisible=False, ephemeral=True)

        role = await self.role
        if role in member.roles:
            try:
                await member.remove_roles(role)
            except NotFound:
                self.role = None
            except Forbidden:
                error = InsufficientPermissions(None, "Manage Roles")
                await interaction.respond(embed=error, ephemeral=True)
                return

################################################################################
    async def _reverse_role_callback(self, interaction: Interaction, member: Member) -> None:

        await interaction.response.defer(invisible=False, ephemeral=True)

        role = await self.role
        try:
            if role in member.roles:
                await member.add_roles(role)
            else:
                await member.remove_roles(role)
        except NotFound:
            self.role = None
        except Forbidden:
            error = InsufficientPermissions(None, "Manage Roles")
            await interaction.respond(embed=error, ephemeral=True)
            return

################################################################################
    async def _limit_role_callback(self, interaction: Interaction, member: Member) -> None:

        await interaction.response.defer(invisible=False, ephemeral=True)

        role = await self.role
        role_limit = self._parent.type_parameter

        if role in member.roles:
            try:
                await member.remove_roles(role)
            except NotFound:
                self.role = None
            except Forbidden:
                error = InsufficientPermissions(None, "Manage Roles")
                await interaction.respond(embed=error, ephemeral=True)
                return
        else:
            id_list = [r._role.id for r in self._parent.roles]
            if len([r for r in member.roles if r.id in id_list]) >= role_limit:
                error = U.make_error(
                    title="__Role Limit Reached__",
                    message=(
                        f"You have already reached the maximum number of roles you "
                        f"can have from this message."
                    ),
                    solution=f"Please remove a role before adding another."
                )
                await interaction.respond(embed=error, ephemeral=True)
                return
            try:
                await member.add_roles(role)
            except NotFound:
                self.role = None
            except Forbidden:
                error = InsufficientPermissions(None, "Manage Roles")
                await interaction.respond(embed=error, ephemeral=True)
                return

################################################################################
    async def _binding_role_callback(self, interaction: Interaction, member: Member) -> None:

        await interaction.response.defer(invisible=False, ephemeral=True)

        role = await self.role
        if role not in member.roles:
            id_list = [r._role.id for r in self._parent.roles]
            if len([r for r in member.roles if r.id in id_list]) > 0:
                error = U.make_error(
                    title="__Role Bound__",
                    message=f"You already have a role from this message.",
                    solution=f"Sorry, no switching roles on this message."
                )
                await interaction.respond(embed=error, ephemeral=True)
                return
            try:
                await member.add_roles(role)
            except NotFound:
                self.role = None
            except Forbidden:
                error = InsufficientPermissions(None, "Manage Roles")
                await interaction.respond(embed=error, ephemeral=True)
                return

################################################################################
