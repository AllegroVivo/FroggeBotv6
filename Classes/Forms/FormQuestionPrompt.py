from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar, Tuple, Any, Dict

from discord import Embed, Interaction

from Assets import BotEmojis
from UI.Common import BasicTextModal, ConfirmCancelView
from UI.Forms import FormPromptStatusView
from Utilities import Utilities as U
from Classes.Common import Identifiable
from Enums import DisplayTime, PromptType

if TYPE_CHECKING:
    from Classes import FormQuestion, FroggeBot
################################################################################

__all__ = ("FormQuestionPrompt",)

FQP = TypeVar("FQP", bound="FormQuestionPrompt")

################################################################################
class FormQuestionPrompt(Identifiable):

    __slots__ = (
        "_parent",
        "_prompt_type",
        "_title",
        "_description",
        "_thumbnail",
        "_active",
        "_show_cancel"
    )

################################################################################
    def __init__(self, parent: FormQuestion, _id: int, _type: int, **kwargs) -> None:

        super().__init__(_id)
        self._parent: FormQuestion = parent

        self._prompt_type: int = _type

        self._title: Optional[str] = kwargs.get("title")
        self._description: Optional[str] = kwargs.get("description")
        self._thumbnail: Optional[str] = kwargs.get("thumbnail")
        self._active: bool = kwargs.get("is_active", True)
        self._show_cancel: bool = kwargs.get("show_cancel", False)

################################################################################
    @classmethod
    def new(cls: Type[FQP], parent: FormQuestion, _type: DisplayTime) -> FQP:

        new_id = parent.bot.api.create_form_question_prompt(parent.id, _type.value)
        return cls(parent, new_id, _type)

################################################################################
    @classmethod
    def load(cls: Type[FQP], parent: FormQuestion, _type, data: Dict[str, Any]) -> FQP:

        return cls(
            parent=parent,
            _type=_type,
            _id=data["id"],
            title=data["title"],
            description=data["description"],
            thumbnail=data["thumbnail_url"],
            show_cancel=data["show_cancel"],
            is_active=data["is_active"]
        )

################################################################################
    @property
    def bot(self) -> FroggeBot:

        return self._parent.bot

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
    def thumbnail(self, value: Optional[str]) -> None:

        self._thumbnail = value
        self.update()

################################################################################
    @property
    def is_active(self) -> bool:

        return self._active

    @is_active.setter
    def is_active(self, value: bool) -> None:

        self._active = value
        self.update()

################################################################################
    @property
    def show_cancel(self) -> bool:
            
        return self._show_cancel
    
    @show_cancel.setter
    def show_cancel(self, value: bool) -> None:
        
        self._show_cancel = value
        self.update()
        
################################################################################
    @property
    def is_filled_out(self) -> bool:
        
        return all([
            self.title is not None,
            self.description is not None,
        ])
    
################################################################################
    def update(self) -> None:

        self.bot.api.update_form_question_prompt(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "title": self.title,
            "description": self.description,
            "thumbnail_url": self.thumbnail,
            "show_cancel": self.show_cancel,
            "is_active": self.is_active
        }

################################################################################
    def status(self) -> Embed:

        return U.make_embed(
            title="__Form Prompt Status__",
            description=(
                f"**[`Display Cancel Button`]:** "
                f"{BotEmojis.Check if self.show_cancel else BotEmojis.Cross}\n"
                f"**[`Title`]:**"
                f"\n`{self.title or 'No Title'}`\n\n"

                f"**[`Description`]:**\n"
                f"```{self.description or 'No Description'}```\n"
            ),
            thumbnail_url=self.thumbnail
        )

################################################################################
    def compile(self) -> Embed:
        
        return U.make_embed(
            title=self.title,
            description=self.description,
            thumbnail_url=self.thumbnail
        )
    
################################################################################
    async def menu(self, interaction: Interaction) -> None:

        embed = self.status()
        view = FormPromptStatusView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def set_title(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Question Prompt Title",
            attribute="Title",
            cur_val=self.title,
            example="e.g. 'Be Aware!'",
            max_length=80,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.title = modal.value

################################################################################
    async def set_description(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Question Prompt Description",
            attribute="Description",
            cur_val=self.description,
            example="e.g. 'This question is very important!'",
            max_length=200,
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
            title="__Set Question Prompt Thumbnail__",
            description=(
                "Please provide an image that you would like to use as the thumbnail.\n\n"

                "This image will be displayed alongside the prompt."
            )
        )
        image_url = await U.wait_for_image(interaction, prompt)
        if image_url is None:
            return

        self.thumbnail = image_url

################################################################################
    async def remove(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Question Prompt__",
            description=(
                "Are you sure you want to remove this question prompt?"
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.delete()

################################################################################
    async def send(self, interaction: Interaction) -> bool:
        
        embed = self.compile()
        view = ConfirmCancelView(interaction.user, show_cancel=self.show_cancel)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
        
        if not view.complete:
            return False
        
        return view.value
        
################################################################################
    async def toggle_cancel_button(self, interaction: Interaction) -> None:
        
        self.show_cancel = not self.show_cancel
        await interaction.respond("** **", delete_after=0.1)
        
################################################################################
    async def toggle_is_active(self, interaction: Interaction) -> None:

        self.is_active = not self.is_active
        await interaction.respond("** **", delete_after=0.1)

################################################################################
