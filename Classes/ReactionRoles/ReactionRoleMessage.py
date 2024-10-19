from __future__ import annotations

from enum import member
from typing import TYPE_CHECKING, List, Optional, Type, TypeVar, Any, Dict

from discord import (
    Message,
    Embed,
    EmbedField,
    Interaction,
    SelectOption,
    User,
    NotFound
)

from Classes.Common import ManagedObject, LazyMessage
from .ReactionRole import ReactionRole
from Utilities import Utilities as U, FroggeColor
from Errors import MaxItemsReached
from UI.ReactionRoles.Views import ReactionRoleMessageStatusView, ReactionRoleView
from UI.Common import BasicTextModal, FroggeSelectView, ConfirmCancelView, CloseMessageView
from Enums import ReactionRoleMessageType

if TYPE_CHECKING:
    from Classes import ReactionRoleManager, FroggeBot, GuildData
    from UI.Common import FroggeView
################################################################################

__all__ = ("ReactionRoleMessage", )

RRM = TypeVar("RRM", bound="ReactionRoleMessage")

################################################################################
class ReactionRoleMessage(ManagedObject):

    __slots__ = (
        "_title",
        "_description",
        "_thumbnail",
        "_roles",
        "_post_msg",
        "_msg_type",
        "_type_param",
        "_color",
    )

    MAX_ROLES = 20

################################################################################
    def __init__(self, mgr: ReactionRoleManager, _id: int, **kwargs) -> None:

        super().__init__(mgr, _id)

        self._mgr: ReactionRoleManager = mgr

        self._title: Optional[str] = kwargs.get("title")
        self._description: Optional[str] = kwargs.get("description")
        self._thumbnail: Optional[str] = kwargs.get("thumbnail")
        self._color: Optional[FroggeColor] = kwargs.get("color",)

        self._msg_type: ReactionRoleMessageType = kwargs.get("msg_type", ReactionRoleMessageType.Normal)
        self._type_param: Optional[int] = kwargs.get("type_param")

        self._roles: List[ReactionRole] = kwargs.get("roles", [])
        self._post_msg: LazyMessage = LazyMessage(self, kwargs.get("post_url"))

################################################################################
    @classmethod
    def new(cls: Type[RRM], mgr: ReactionRoleManager) -> RRM:

        new_data = mgr.bot.api.create_reaction_role_message(mgr.guild_id)
        return cls(mgr, new_data["id"])

################################################################################
    @classmethod
    def load(cls: Type[RRM], mgr: ReactionRoleManager, data: Dict[str, Any]) -> RRM:

        self: RRM = cls.__new__(cls)

        self._id = data["id"]
        self._mgr = mgr

        self._title = data["title"]
        self._description = data["description"]
        self._thumbnail = data["thumbnail_url"]
        self._color = FroggeColor(data["color"]) if data["color"] is not None else None

        self._msg_type = ReactionRoleMessageType(data["msg_type"])
        self._type_param = data["type_param"]

        self._roles = [ReactionRole.load(self, r) for r in data["roles"]]
        self._post_msg = LazyMessage(self, data.get("post_url"))

        return self

################################################################################
    def __getitem__(self, role_id: int) -> Optional[ReactionRole]:

        return next((r for r in self.roles if r.id == int(role_id)), None)

################################################################################
    @property
    def bot(self) -> FroggeBot:

        return self._mgr.bot

################################################################################
    @property
    def guild(self) -> GuildData:

        return self._mgr.guild

################################################################################
    @property
    def title(self) -> Optional[str]:

        return self._title

    @title.setter
    def title(self, value: str) -> None:

        self._title = value
        self.update()

################################################################################
    @property
    def description(self) -> Optional[str]:

        return self._description

    @description.setter
    def description(self, value: str) -> None:

        self._description = value
        self.update()

################################################################################
    @property
    def thumbnail(self) -> Optional[str]:

        return self._thumbnail

    @thumbnail.setter
    def thumbnail(self, value: str) -> None:

        self._thumbnail = value
        self.update()

################################################################################
    @property
    def color(self) -> Optional[FroggeColor]:

        return self._color

    @color.setter
    def color(self, value: Optional[FroggeColor]) -> None:

        self._color = value
        self.update()

################################################################################
    @property
    def roles(self) -> List[ReactionRole]:

        return self._roles

################################################################################
    @property
    async def post_message(self) -> Optional[Message]:

        return await self._post_msg.get()

    @post_message.setter
    def post_message(self, value: Message) -> None:

        self._post_msg.set(value)

################################################################################
    @property
    def message_type(self) -> ReactionRoleMessageType:

        return self._msg_type

    @message_type.setter
    def message_type(self, value: ReactionRoleMessageType) -> None:

        self._msg_type = value
        self.update()

################################################################################
    @property
    def type_parameter(self) -> Optional[int]:

        return self._type_param

    @type_parameter.setter
    def type_parameter(self, value: Optional[int]) -> None:

        self._type_param = value
        self.update()

################################################################################
    def update(self) -> None:

        self.bot.api.update_reaction_role_message(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "title": self.title,
            "description": self.description,
            "thumbnail_url": self.thumbnail,
            "post_url": self._post_msg.id,
            "msg_type": self.message_type.value,
            "type_param": self.type_parameter,
            "color": self.color.value if self.color is not None else None,
        }

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_reaction_role_message(self.id)
        self._mgr._managed.remove(self)

################################################################################
    async def status(self) -> Embed:

        description = (
            f"**Message Type:** [`{self.message_type.proper_name}`]\n"
            f"*({self.message_type.description})*\n"
            f"{U.draw_line(text=self.message_type.description)}\n"
            f"**Title:**\n```{self._title or 'Not Set'}```\n"
            f"**Description:**\n```{self._description or 'Not Set'}```\n"
        )

        role_str = ""
        for r in self.roles:
            if r._role.id is None:
                continue
            role = await r.role
            role_str += f"**{str(r.emoji) if r.emoji else '[]'}** - {role.mention}\n"

        return U.make_embed(
            title="__Reaction Role Message Status__",
            description=description,
            thumbnail_url=self.thumbnail,
            fields=[
                EmbedField(
                    name="Roles",
                    value=role_str or "`No Roles Set-Up`",
                    inline=False
                )
            ]
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return ReactionRoleMessageStatusView(user, self)

################################################################################
    async def compile(self) -> Embed:

        role_str = ""
        for r in self.roles:
            if r._role.id is None:
                continue
            role = await r.role
            role_str += f"* {r.emoji or '[]'} - {role.mention}\n"

        return U.make_embed(
            color=self.color or FroggeColor.embed_background(),
            title=self.title or "Untitled Reaction Role Message",
            description=self.description,
            thumbnail_url=self.thumbnail,
            fields=[
                EmbedField(
                    name="**__Role Options__**",
                    value=role_str or "`No Roles Set-Up`",
                    inline=False
                )
            ],
            footer_text=self.message_type.description
        )

################################################################################
    async def set_title(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Reaction Role Message Title",
            attribute="Title",
            cur_val=self.title,
            example="eg 'Select your Preferred Pronouns'",
            max_length=100
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.title = modal.value

################################################################################
    async def set_description(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Reaction Role Message Description",
            attribute="Description",
            cur_val=self.description,
            example="eg 'React to the Emoji that Best Represents You'",
            max_length=500,
            multiline=True
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.description = modal.value

################################################################################
    async def set_thumbnail(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Reaction Role Message Thumbnail__",
            description="Please provide an image to use as the thumbnail for this message"
        )

        image_url = await U.wait_for_image(interaction, prompt)
        if image_url is None:
            return

        self.thumbnail = image_url

################################################################################
    async def add_role(self, interaction: Interaction) -> None:

        if len(self._roles) >= self.MAX_ROLES:
            error = MaxItemsReached("Reaction Roles", self.MAX_ROLES)
            await interaction.respond(embed=error, ephemeral=True)
            return

        role = ReactionRole.new(self)
        self._roles.append(role)

        await role.menu(interaction)

################################################################################
    async def modify_role(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Modify Reaction Role__",
            description="Please select the role you would like to modify"
        )
        view = FroggeSelectView(interaction.user, [r.select_option() for r in self.roles])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        role = self[view.value]
        await role.menu(interaction)

################################################################################
    async def remove_role(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Reaction Role__",
            description="Please select the role you would like to remove"
        )
        view = FroggeSelectView(interaction.user, [r.select_option() for r in self.roles])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        role = self[view.value]
        await role.remove(interaction)

################################################################################
    def select_option(self) -> SelectOption:

        return SelectOption(
            label=self.title or "Untitled Reaction Role Message",
            value=str(self.id)
        )

################################################################################
    async def remove(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Reaction Role Message__",
            description="Are you sure you want to remove this reaction role message?"
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        post_message = await self.post_message
        if post_message is not None:
            try:
                await post_message.delete()
            except NotFound:
                pass

        self.delete()

################################################################################
    async def post(self, interaction: Interaction) -> None:

        post_channel = await self.manager.channel  # type: ignore
        if post_channel is None:
            error = U.make_error(
                title="Reaction Roles Posting Channel Not Set",
                message="The reaction roles post channel has not been set for this server.",
                solution=(
                    "Please set the channel where you would like to post reaction roles by "
                    "using the `Set Reaction Role Post Channel` button."
                )
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        if await self.update_post_components():
            return

        view = ReactionRoleView(self.roles)
        self.bot.add_view(view)

        self.post_message = await post_channel.send(embed=await self.compile(), view=view)

        success = U.make_embed(
            title="__Reaction Role Message Posted__",
            description=(
                "The reaction role message has been successfully posted.\n\n"
                
                f"**[Jump to Message]({self._post_msg.id})**"
            )
        )
        view = CloseMessageView(interaction.user)

        await interaction.respond(embed=success, view=view)
        await view.wait()

################################################################################
    async def update_post_components(self) -> bool:

        post_message = await self.post_message
        if post_message is None:
            return False

        view = ReactionRoleView(self.roles)
        self.bot.add_view(view)

        try:
            await post_message.edit(embed=await self.compile(), view=view)
        except NotFound:
            self.post_message = None
            return False
        else:
            return True

################################################################################
    async def set_message_type(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Reaction Role Message Type__",
            description="Please select the type of reaction role message you would like to create."
        )
        view = FroggeSelectView(interaction.user, ReactionRoleMessageType.select_options())

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.message_type = ReactionRoleMessageType(int(view.value))

################################################################################
