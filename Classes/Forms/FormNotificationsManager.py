from __future__ import annotations

from typing import TYPE_CHECKING, List, Type, TypeVar

from discord import Role, User, Embed, EmbedField, Interaction, SelectOption

from Classes.Common import LazyRole, LazyUser
from Utilities import Utilities as U
from UI.Forms import FormNotificationsManagerView
from Errors import MaxItemsReached
from UI.Common import FroggeSelectView

if TYPE_CHECKING:
    from Classes import Form, GuildData
################################################################################

__all__ = ("FormNotificationsManager", )

FNM = TypeVar("FNM", bound="FormNotificationsManager")

################################################################################
class FormNotificationsManager:

    __slots__ = (
        "_parent",
        "_roles",
        "_users",
    )

    MAX_NOTIFICATIONS = 20

################################################################################
    def __init__(self, parent: Form, **kwargs) -> None:

        self._parent: Form = parent

        self._roles: List[LazyRole] = kwargs.get("roles", [])
        self._users: List[LazyUser] = kwargs.get("users", [])

################################################################################
    @classmethod
    def load(cls: FNM, parent: Form, role_data: List[int], user_data: List[int]) -> FNM:

        self: FNM = cls.__new__(cls)

        self._parent = parent

        self._roles = [LazyRole(self, role_id) for role_id in role_data]
        self._users = [LazyUser(self, user_id) for user_id in user_data]

        return self

################################################################################
    @property
    def guild(self) -> GuildData:

        return self._parent.guild

################################################################################
    @property
    async def roles(self) -> List[Role]:

        return [await role.get() for role in self._roles]

################################################################################
    @property
    async def users(self) -> List[User]:

        return [await user.get() for user in self._users]

################################################################################
    def update(self) -> None:

        self._parent.update()

################################################################################
    async def status(self) -> Embed:

        roles = await self.roles
        users = await self.users
        role_string = "\n".join([f'- {r.mention}' for r in roles])
        user_string = "\n".join([f'- {u.mention}' for u in users])
        
        
        return U.make_embed(
            title="__Form Notifications__",
            description="Here are the roles and users that will be notified when a form is submitted.",
            fields=[
                EmbedField(
                    name="__Roles__",
                    value=role_string,
                    inline=True,
                ),
                EmbedField(
                    name="__Users__",
                    value=user_string,
                    inline=True,
                )
            ]
        )

################################################################################
    async def menu(self, interaction: Interaction) -> None:

        embed = await self.status()
        view = FormNotificationsManagerView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def add_user(self, interaction: Interaction) -> None:

        if len(self._users) >= self.MAX_NOTIFICATIONS:
            error = MaxItemsReached("Notification Parties", self.MAX_NOTIFICATIONS)
            await interaction.respond(embed=error, ephemeral=True)
            return

        prompt = U.make_embed(
            title="__Add User__",
            description="Please mention the user you would like to add to the notification list."
        )

        user = await U.listen_for(interaction, prompt, U.MentionableType.User)
        if user is None:
            return

        self._users.append(LazyUser(self, user.id))
        self.update()

################################################################################
    async def add_role(self, interaction: Interaction) -> None:

        if len(self._roles) >= self.MAX_NOTIFICATIONS:
            error = MaxItemsReached("Notification Parties", self.MAX_NOTIFICATIONS)
            await interaction.respond(embed=error, ephemeral=True)
            return

        prompt = U.make_embed(
            title="__Add Role__",
            description="Please mention the role you would like to add to the notification list."
        )

        role = await U.listen_for(interaction, prompt, U.MentionableType.Role)
        if role is None:
            return

        self._roles.append(LazyRole(self, role.id))
        self.update()

################################################################################
    async def remove_user(self, interaction: Interaction) -> None:

        users = await self.users
        options = [
            SelectOption(
                label=u.display_name,
                value=str(u.id)
            ) for u in users
        ]

        prompt = U.make_embed(
            title="__Remove User__",
            description="Please select the user you would like to remove from the notification list."
        )
        view = FroggeSelectView(interaction.user, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self._users = [u for u in self._users if u.id != int(view.value)]
        self.update()

################################################################################
    async def remove_role(self, interaction: Interaction) -> None:

        roles = await self.roles
        options = [
            SelectOption(
                label=r.name,
                value=str(r.id)
            ) for r in roles
        ]

        prompt = U.make_embed(
            title="__Remove Role__",
            description="Please select the role you would like to remove from the notification list."
        )
        view = FroggeSelectView(interaction.user, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self._roles = [r for r in self._roles if r.id != int(view.value)]
        self.update()

################################################################################
