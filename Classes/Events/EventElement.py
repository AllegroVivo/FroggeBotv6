from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar, Any, Dict

from discord import Message, Embed, Interaction, EmbedField

from Classes.Common import Identifiable, LazyMessage
from Enums import ElementType
from logger import log
from Utilities import Utilities as U
from UI.Common import BasicTextModal, ConfirmCancelView
from UI.Events import EventElementStatusView

if TYPE_CHECKING:
    from Classes import Event, FroggeBot, GuildData
################################################################################

__all__ = ("EventElement", )

EE = TypeVar("EE", bound="EventElement")

################################################################################
class EventElement(Identifiable):

    __slots__ = (
        "_parent",
        "_type",
        "_title",
        "_value",
        "_post_msg",
    )

################################################################################
    def __init__(self, parent: Event, _type: ElementType, _id: int, **kwargs) -> None:

        super().__init__(_id)

        self._parent: Event = parent
        self._type: ElementType = _type

        self._title: Optional[str] = kwargs.get("title")
        self._value: Optional[str] = kwargs.get("value")
        self._post_msg: LazyMessage = LazyMessage(self, kwargs.get("post_url"))

################################################################################
    @classmethod
    def new(cls: Type[EE], parent: Event, _type: ElementType) -> EE:

        data = parent.bot.api.create_event_element(parent.id, _type.value)
        return cls(parent, _type, data["id"])

################################################################################
    @classmethod
    def load(cls: Type[EE], parent: Event, data: Dict[str, Any]) -> EE:

        return cls(
            parent=parent,
            _id=data["id"],
            _type=ElementType(data["element_type"]),
            title=data["title"],
            value=data["value"],
            post_url=data["post_url"]
        )

################################################################################
    @classmethod
    def from_template(cls: Type[EE], parent: Event, other: TemplateSecondary) -> EE:

        new_data = parent.bot.api.create_event_element(parent.id, other.message_type.value)
        return cls(
            parent=parent,
            _id=new_data["id"],
            type=other.message_type,
            title=other.title,
            value=other.value
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
    def type(self) -> ElementType:

        return self._type

################################################################################
    @property
    def title(self) -> Optional[str]:

        if self._title is not None:
            return self._title

        idx = self._parent.elements[self._type].index(self)
        return f"{self._type.proper_name} {idx + 1}"

    @title.setter
    def title(self, value: str) -> None:

        self._title = value
        self.update()

################################################################################
    @property
    def value(self) -> Optional[str]:

        return self._value

    @value.setter
    def value(self, value: str) -> None:

        self._value = value
        self.update()

################################################################################
    @property
    async def post_message(self) -> Optional[Message]:

        return await self._post_msg.get()

    @post_message.setter
    def post_message(self, value: Optional[Message]) -> None:

        self._post_msg.set(value)

################################################################################
    def update(self) -> None:

        self.bot.api.update_event_element(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "title": self._title,
            "value": self._value,
            "post_url": self._post_msg.id
        }

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_event_element(self.id)

        self._parent.elements[self._type].remove(self)
        if not self._parent.elements[self._type]:
            del self._parent.elements[self._type]

################################################################################
    def status(self) -> Embed:

        return U.make_embed(
            title=f"Secondary Element: {self.type.proper_name}",
            description=(
                "**Element Title:**\n"
                f"`{self.title}`"
            ),
            fields=[
                EmbedField(
                    name="Value",
                    value=(
                        f"```{self.value}```"
                    ) if self.value else "`Not Set`",
                    inline=False
                ),
            ]
        )

################################################################################
    async def menu(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Secondary Element Menu: {self.type.proper_name}")

        embed = self.status()
        view = EventElementStatusView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def set_title(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Set Element Title: {self.type.proper_name}")

        modal = BasicTextModal(
            title="Set Element Title",
            attribute="Title",
            cur_val=self._title,
            max_length=80,
            required=False
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            log.debug(self.guild, "Modal Cancelled")
            return

        self.title = modal.value

        log.info(self.guild, f"Element Title Set: {self.title}")

################################################################################
    async def set_value(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Set Element Value: {self.type.proper_name}")

        modal = BasicTextModal(
            title="Set Element Value",
            attribute="Value",
            cur_val=self.value,
            max_length=500,
            required=False,
            multiline=True
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            log.debug(self.guild, "Modal Cancelled")
            return

        self.value = modal.value

        log.info(self.guild, f"Element Value Set: {self.value}")

################################################################################
    async def remove(self, interaction: Interaction) -> bool:

        log.info(self.guild, f"Remove Element: {self.type.proper_name}")

        prompt = U.make_embed(
            title="__Remove Element__",
            description=(
                f"Are you sure you want to remove the {self.type.proper_name}?"
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "Remove Cancelled")
            return False

        self.delete()

        log.info(self.guild, f"Element Removed: {self.type.proper_name}")

        return True

################################################################################

