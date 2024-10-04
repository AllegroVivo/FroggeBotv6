from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any, Dict, Type, TypeVar

from Classes.Common import LazyUser
from discord import PartialEmoji, Interaction, User
from UI.Common import BasicTextModal, BasicNumberModal
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import Room, FroggeBot, GuildData
################################################################################

__all__ = ("RoomDetails", )

RD = TypeVar("RD", bound="RoomDetails")

################################################################################
class RoomDetails:

    __slots__ = (
        "_parent",
        "_index",
        "_owner",
        "_theme",
        "_description",
        "_locked",
        "_emoji",
        "_disabled",
        "_name",
    )

################################################################################
    def __init__(self, parent: Room, index: int, **kwargs) -> None:

        self._parent: Room = parent
        self._index: int = index

        self._owner: LazyUser = LazyUser(self, kwargs.get("owner_id"))
        self._name: Optional[str] = kwargs.get("name")
        self._theme: Optional[str] = kwargs.get("theme")
        self._description: Optional[str] = kwargs.get("description")

        self._locked: bool = kwargs.get("locked", False)
        self._emoji: Optional[PartialEmoji] = kwargs.get("emoji")
        self._disabled: bool = kwargs.get("disabled", False)

################################################################################
    @classmethod
    def load(cls: Type[RD], parent: Room, data: Dict[str, Any]) -> RD:

        return cls(
            parent=parent,
            index=data["index"],
            owner_id=data["owner"],
            name=data["name"],
            theme=data["theme"],
            description=data["description"],
            locked=data["locked"],
            emoji=PartialEmoji.from_str(data["emoji"]) if data["emoji"] else None,
            disabled=data["disabled"]
        )

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
    def index(self) -> Optional[int]:

        return self._index

    @index.setter
    def index(self, value: Optional[int]):

        self._index = value
        self.update()

################################################################################
    @property
    async def owner(self) -> Optional[User]:

        return await self._owner.get()

    @owner.setter
    def owner(self, value: Optional[User]):

        self._owner.set(value)

################################################################################
    @property
    def theme(self) -> Optional[str]:

        return self._theme

    @theme.setter
    def theme(self, value: Optional[str]):

        self._theme = value
        self.update()

################################################################################
    @property
    def name(self) -> Optional[str]:

        return self._name

    @name.setter
    def name(self, value: Optional[str]):

        self._name = value
        self.update()

################################################################################
    @property
    def description(self) -> Optional[str]:

        return self._description

    @description.setter
    def description(self, value: Optional[str]):

        self._description = value
        self.update()

################################################################################
    @property
    def locked(self) -> bool:

        return self._locked

    @locked.setter
    def locked(self, value: bool):

        self._locked = value
        self.update()

################################################################################
    @property
    def emoji(self) -> Optional[PartialEmoji]:

        return self._emoji

    @emoji.setter
    def emoji(self, value: Optional[PartialEmoji]):

        self._emoji = value
        self.update()

################################################################################
    @property
    def disabled(self) -> bool:

        return self._disabled

    @disabled.setter
    def disabled(self, value: bool):

        self._disabled = value
        self.update()

################################################################################
    def update(self) -> None:

        self.bot.api.update_room_details(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "index": self.index,
            "owner": self._owner.id,
            "name": self.name,
            "theme": self.theme,
            "description": self.description,
            "locked": self.locked,
            "emoji": str(self.emoji) if self.emoji else None,
            "disabled": self.disabled
        }

################################################################################
    async def set_name(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Room Name",
            attribute="Name",
            cur_val=self.name,
            example="eg. 'Super Sexy Snuggle Room'",
            max_length=50,
            required=False
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.name = modal.value

################################################################################
    async def set_theme(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Room Theme",
            attribute="Theme",
            cur_val=self.theme,
            example="eg. 'Romantic Getaway'",
            max_length=80,
            required=False
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.theme = modal.value

################################################################################
    async def set_owner(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Room Owner__",
            description=(
                "Please respond with the user you'd like to set as the owner of this room."
            )
        )
        owner = await U.listen_for(interaction, prompt, U.MentionableType.User)
        if owner is None:
            return

        self.owner = owner

################################################################################
    async def set_description(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Room Description",
            attribute="Description",
            cur_val=self.description,
            example="eg. 'A cozy room for two to snuggle up and watch a movie.'",
            max_length=200,
            required=False,
            multiline=True
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.description = modal.value

################################################################################
    async def toggle_locked(self, interaction: Interaction) -> None:

        self.locked = not self.locked
        await interaction.respond("** **", delete_after=0.1)

################################################################################
    async def set_emoji(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Room Emoji__",
            description=(
                "Please respond with the emoji you'd like to use for this room."
            )
        )
        emoji = await U.listen_for(interaction, prompt, U.MentionableType.Emoji)
        if emoji is None:
            return

        self.emoji = emoji

################################################################################
    async def toggle_disabled(self, interaction: Interaction) -> None:

        self.disabled = not self.disabled
        await interaction.respond("** **", delete_after=0.1)

################################################################################
    async def set_index(self, interaction: Interaction) -> None:

        modal = BasicNumberModal(
            title="Set Room Index",
            attribute="Index",
            cur_val=self.index,
            example="eg. '007'"
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.index = modal.value

################################################################################
