from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar, Tuple, Any, Dict

from discord import PartialEmoji, Interaction, Embed, EmbedField, SelectOption

from UI.Common import ConfirmCancelView, BasicTextModal
from UI.Forms import FormOptionStatusView
from Utilities import Utilities as U
from Classes.Common import Identifiable

if TYPE_CHECKING:
    from Classes import FormQuestion, FroggeBot
################################################################################

__all__ = ("FormOption", )

FO = TypeVar("FO", bound="FormOption")

################################################################################
class FormOption(Identifiable):

    __slots__ = (
        "_parent",
        "_label",
        "_description",
        "_value",
        "_emoji"
    )
    
################################################################################
    def __init__(self, parent: FormQuestion, _id: int, **kwargs) -> None:

        super().__init__(_id)

        self._parent: FormQuestion = parent
        
        self._label: Optional[str] = kwargs.get("label")
        self._description: Optional[str] = kwargs.get("description")
        self._value: Optional[str] = kwargs.get("value")
        self._emoji: Optional[PartialEmoji] = kwargs.get("emoji")
    
################################################################################
    @classmethod
    def new(cls: Type[FO], parent: FormQuestion) -> FO:
        
        new_data = parent.bot.api.create_form_option(parent.id)
        return cls(parent, new_data["id"])

################################################################################
    @classmethod
    def load(cls: Type[FO], parent: FormQuestion, data: Dict[str, Any]) -> FO:
        
        return cls(
            parent=parent,
            _id=data["id"],
            label=data["label"],
            description=data["description"],
            value=data["value"],
            emoji=PartialEmoji.from_str(data["emoji"]) if data["emoji"] else None
        )
    
################################################################################
    @property
    def bot(self) -> FroggeBot:
        
        return self._parent.bot
    
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
    def description(self) -> Optional[str]:
        
        return self._description
    
    @description.setter
    def description(self, value: Optional[str]) -> None:
        
        self._description = value
        self.update()
        
################################################################################
    @property
    def value(self) -> Optional[str]:
        
        return self._value or self.label
    
    @value.setter
    def value(self, value: Optional[str]) -> None:
        
        self._value = value
        self.update()
        
################################################################################
    @property
    def emoji(self) -> Optional[PartialEmoji]:
        
        return self._emoji
    
    @emoji.setter
    def emoji(self, value: Optional[PartialEmoji]) -> None:
        
        self._emoji = value
        self.update()
        
################################################################################
    def update(self) -> None:
        
        self.bot.api.update_form_option(self)
        
################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "label": self.label,
            "description": self.description,
            "value": self.value,
            "emoji": str(self.emoji) if self.emoji else None
        }

################################################################################
    def delete(self) -> None:
        
        self.bot.api.delete_form_option(self.id)
        self._parent.options.remove(self)
        
################################################################################
    def status(self) -> Embed:

        return U.make_embed(
            title="__Application Option Status__",
            fields=[
                EmbedField(
                    name="__Label__",
                    value=self.label if self.label is not None else "`Not Set`",
                    inline=True
                ),
                EmbedField(
                    name="__Emoji__",
                    value=(
                        str(self.emoji) if self.emoji is not None else "`Not Set`"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__Underlying Value__",
                    value=self.value if self.value is not None else self.label or "`Not Set`",
                    inline=False
                ),
                EmbedField(
                    name="__Description__",
                    value=self.description if self.description is not None else "`Not Set`",
                    inline=False
                ),
            ]
        )
    
################################################################################
    async def menu(self, interaction: Interaction) -> None:

        embed = self.status()
        view = FormOptionStatusView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
        
################################################################################
    async def remove(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Option__",
            description=(
                "Are you sure you want to remove this option from the question?\n\n"

                "This action is irreversible."
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or not view.value:
            return

        self.delete()

################################################################################
    async def set_label(self, interaction: Interaction) -> None:
        
        modal = BasicTextModal(
            title="Enter Option Label",
            attribute="Label",
            example='e.g. "Yes"',
            cur_val=self.label,
            max_length=80
        )
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        self.label = modal.value
    
################################################################################
    async def set_description(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Enter Option Description",
            attribute="Description",
            example="eg. 'This option is for users who are over 18.'",
            cur_val=self.description,
            max_length=80
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.description = modal.value
    
################################################################################
    async def set_value(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Enter Option Value",
            attribute="Value",
            cur_val=self.value,
            max_length=80
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.value = modal.value
    
################################################################################
    async def set_emoji(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Set Emoji__",
            description=(
                "Please send the emoji you would like to use for this option."
            )
        )
        emoji = await U.listen_for(interaction, prompt, U.MentionableType.Emoji)
        if emoji is None:
            return
        
        self.emoji = emoji
    
################################################################################
    def select_option(self) -> SelectOption:

        return SelectOption(
            label=self.label or "Question Label Not Set",
            value=str(self.id),
            description=self.description,
            emoji=self.emoji
        )

################################################################################
