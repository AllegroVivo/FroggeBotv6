from __future__ import annotations

from typing import TYPE_CHECKING, Optional, TypeVar, Type, Any, Dict
from discord import EmbedField, Embed, Interaction, SelectOption

from Classes.Common import Identifiable
from Utilities import Utilities as U
from UI.Embeds import EmbedFieldStatusView
from UI.Common import BasicTextModal, ConfirmCancelView

if TYPE_CHECKING:
    from Classes import FroggeEmbed, FroggeBot
################################################################################

__all__ = ("FroggeEmbedField", )

FEF = TypeVar("FEF", bound="FroggeEmbedField")

################################################################################
class FroggeEmbedField(Identifiable):

    __slots__ = (
        "_parent",
        "_name",
        "_value",
        "_inline",
        "_order",
    )

################################################################################
    def __init__(self, parent: FroggeEmbed, _id: int, order : int, **kwargs) -> None:

        super().__init__(_id)

        self._parent: FroggeEmbed = parent
        self._order: int = order

        self._name: Optional[str] = kwargs.get("name")
        self._value: Optional[str] = kwargs.get("field")
        self._inline: bool = kwargs.get("inline", False)

################################################################################
    @classmethod
    def new(cls: Type[FEF], parent: FroggeEmbed) -> FEF:

        new_data = parent.bot.api.create_embed_field(parent.id)
        return cls(parent=parent, _id=new_data["id"], order=new_data["sort_order"])

################################################################################
    @classmethod
    def load(cls: Type[FEF], parent: FroggeEmbed, data: Dict[str, Any]) -> FEF:

        return cls(
            parent=parent,
            _id=data["id"],
            order=data["sort_order"],
            name=data["name"],
            value=data["value"],
            inline=data["inline"]
        )

################################################################################
    @property
    def bot(self) -> FroggeBot:

        return self._parent.bot

################################################################################
    @property
    def name(self) -> Optional[str]:

        return self._name

    @name.setter
    def name(self, value: Optional[str]) -> None:

        self._name = value
        self.update()

################################################################################
    @property
    def value(self) -> Optional[str]:

        return self._value

    @value.setter
    def value(self, value: Optional[str]) -> None:

        self._value = value
        self.update()

################################################################################
    @property
    def inline(self) -> bool:

        return self._inline

    @inline.setter
    def inline(self, value: bool) -> None:

        self._inline = value
        self.update()

################################################################################
    @property
    def order(self) -> int:

        return self._order

    @order.setter
    def order(self, value: int) -> None:

        self._order = value
        self.update()

################################################################################
    def update(self) -> None:

        self.bot.api.update_embed_field(self)

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_embed_field(self.id)
        self._parent.fields.remove(self)

################################################################################
    def to_dict(self) -> dict:

        return {
            "name": self.name,
            "value": self.value,
            "inline": self.inline,
            "sort_order": self.order
        }

################################################################################
    def compile(self) -> EmbedField:

        return EmbedField(
            name=self.name or "** **",
            value=self.value or "** **",
            inline=self.inline
        )

################################################################################
    def status(self) -> Embed:

        return U.make_embed(
            title="__Embed Header Status__",
            description=(
                "**Field Title:**\n"
                f"{self.name or '`Not Set`'}\n\n"

                f"**Field Value:**\n"
                f"{self.value or '`Not Set`'}\n\n"

                "**Inline:**\n"
                f"[`{self.inline}`]"
            ),
        )

################################################################################
    async def menu(self, interaction: Interaction) -> None:

        embed = self.status()
        view = EmbedFieldStatusView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def set_name(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Field Title",
            attribute="Title",
            example="eg. Rule #1",
            cur_val=self.name,
            max_length=256,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.name = modal.value

################################################################################
    async def set_value(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Field Value",
            attribute="Value",
            example="eg. No spamming",
            cur_val=self.value,
            max_length=1024,
            multiline=True
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.value = modal.value

################################################################################
    async def toggle_inline(self, interaction: Interaction) -> None:

        self.inline = not self.inline
        await interaction.respond("** **", delete_after=0.1)

################################################################################
    def select_option(self) -> SelectOption:

        return SelectOption(
            label=self.name or "Title Not Set",
            value=str(self.id),
            description=U.string_clamp(self.value or "Value Not Set", 50),
        )

################################################################################
    async def remove(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Delete Field__",
            description="Are you sure you want to delete this field?",
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.delete()

################################################################################
