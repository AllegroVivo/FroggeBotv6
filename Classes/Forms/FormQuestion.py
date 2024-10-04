from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List, Dict, Type, TypeVar, Any, Tuple

from discord import Embed, EmbedField, Interaction, SelectOption, User
from discord.ext.pages import Page

from Assets import BotEmojis
from Enums import UIComponentType, DisplayTime
from Errors import MaxItemsReached
from UI.Common import FroggeSelectView, BasicTextModal, ConfirmCancelView
from UI.Forms import FormQuestionStatusView, FormPageResponseView
from Utilities import Utilities as U
from .FormOption import FormOption
from .FormQuestionPrompt import FormQuestionPrompt
from Classes.Common import Identifiable

if TYPE_CHECKING:
    from Classes import Form, FroggeBot
################################################################################

__all__ = ("FormQuestion", )

FQ = TypeVar("FQ", bound="FormQuestion")

################################################################################
class FormQuestion(Identifiable):

    __slots__ = (
        "_parent",
        "_order",
        "_primary",
        "_secondary",
        "_ui_type",
        "_required",
        "_options",
        "_responses",
        "_pre_prompt",
        "_post_prompt",
    )

    MAX_OPTIONS = 20

################################################################################
    def __init__(self, parent: Form, _id: int, order: int, **kwargs) -> None:

        super().__init__(_id)

        self._parent: Form = parent
        self._order: int = order

        self._primary: str = kwargs.get("primary")
        self._secondary: Optional[str] = kwargs.get("secondary")
        self._ui_type: UIComponentType = kwargs.get("ui_type", UIComponentType.ShortText)
        self._required: bool = kwargs.get("required", False)
        self._options: List[FormOption] = kwargs.get("options", [])

        self._responses: Dict[int, List[str]] = kwargs.get("responses", {})
        self._pre_prompt: FormQuestionPrompt = kwargs.get("pre_prompt")
        self._post_prompt: FormQuestionPrompt = kwargs.get("post_prompt")

################################################################################
    @classmethod
    def new(cls: Type[FQ], parent: Form) -> FQ:

        data = parent.bot.api.create_form_question(parent.id)

        self: FQ = cls.__new__(cls)

        self._id = data["id"]
        self._parent = parent
        self._order = data["sort_order"]

        self._primary = data["primary_text"]
        self._secondary = data["secondary_text"]
        self._ui_type = UIComponentType(data["ui_type"])
        self._required = data["required"]

        self._options = []
        self._responses = {}

        for prompt in data["prompts"]:
            if prompt["prompt_type"] == 1:
                self._pre_prompt = FormQuestionPrompt.load(self, DisplayTime.Before, prompt)
            elif prompt["prompt_type"] == 2:
                self._post_prompt = FormQuestionPrompt.load(self, DisplayTime.After, prompt)

        return self

################################################################################
    @classmethod
    def load(cls: Type[FQ], parent: Form, data: Dict[str, Any]) -> FQ:

        self: FQ = cls.__new__(cls)

        self._id = data["id"]
        self._parent = parent
        self._order = data["sort_order"]

        self._primary = data["primary_text"]
        self._secondary = data["secondary_text"]
        self._ui_type = UIComponentType(data["ui_type"])
        self._required = data["required"]

        self._options = [FormOption.load(self, o) for o in data["options"]]
        self._responses = {
            response["user_id"]: response["values"]
            for response in data["responses"]
        }

        for prompt in data["prompts"]:
            if prompt["prompt_type"] == 1:
                self._pre_prompt = FormQuestionPrompt.load(self, DisplayTime.Before, prompt)
            elif prompt["prompt_type"] == 2:
                self._post_prompt = FormQuestionPrompt.load(self, DisplayTime.After, prompt)

        return self

################################################################################
    def __getitem__(self, user_id: int) -> Optional[List[str]]:

        return self._responses.get(user_id, None)

################################################################################
    @property
    def bot(self) -> FroggeBot:

        return self._parent.bot

################################################################################
    @property
    def order(self) -> int:

        return self._order

    @order.setter
    def order(self, value: int) -> None:

        self._order = value
        self.update()

################################################################################
    @property
    def primary_text(self) -> str:

        return self._primary

    @primary_text.setter
    def primary_text(self, value: str) -> None:

        self._primary = value
        self.update()

################################################################################
    @property
    def secondary_text(self) -> Optional[str]:

        return self._secondary

    @secondary_text.setter
    def secondary_text(self, value: Optional[str]) -> None:

        self._secondary = value
        self.update()

################################################################################
    @property
    def ui_type(self) -> UIComponentType:

        return self._ui_type

    @ui_type.setter
    def ui_type(self, value: UIComponentType) -> None:

        self._ui_type = value
        self.update()

################################################################################
    @property
    def required(self) -> bool:

        return self._required

    @required.setter
    def required(self, value: bool) -> None:

        self._required = value
        self.update()

################################################################################
    @property
    def options(self) -> List[FormOption]:

        return self._options

################################################################################
    @property
    def responses(self) -> Dict[int, List[str]]:

        return self._responses

################################################################################
    @property
    def pre_prompt(self) -> FormQuestionPrompt:

        return self._pre_prompt

    @property
    def post_prompt(self) -> FormQuestionPrompt:

        return self._post_prompt

################################################################################
    def update(self) -> None:

        self.bot.api.update_form_question(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "id": self.id,
            "sort_order": self.order,
            "primary_text": self.primary_text,
            "secondary_text": self.secondary_text,
            "ui_type": self.ui_type.value,
            "required": self.required,
        }

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_form_question(self.id)
        self._parent.questions.remove(self)

################################################################################
    def status(self) -> Embed:

        pre_emoji = BotEmojis.CheckGreen if self._pre_prompt.is_active else BotEmojis.Cross
        post_emoji = BotEmojis.CheckGreen if self._post_prompt.is_active else BotEmojis.Cross

        fields = [
            EmbedField(
                name="UI Type",
                value=f"`{self.ui_type.proper_name}`",
                inline=True
            ),
            EmbedField(
                name="Required",
                value=str(BotEmojis.Check if self.required else BotEmojis.Cross),
                inline=True
            ),
            EmbedField(
                name="Question Prompts",
                value=(
                    f"**Pre-Prompt Enabled:** {str(pre_emoji)}\n"
                    f"**Post-Prompt Enabled:** {str(post_emoji)}"
                ),
                inline=True
            ),
            EmbedField(
                name="__Primary Text__",
                value=f"`{self.primary_text}`",
                inline=False
            ),
            EmbedField(
                name="__Secondary Text__",
                value=f"```{self.secondary_text}```",
                inline=False
            )
        ]

        if self.ui_type in (UIComponentType.SelectMenu, UIComponentType.MultiSelect):
            fields.append(
                EmbedField(
                    name="__Options__",
                    value="\n".join(
                        f"{str(option.emoji) if option.emoji else ''} "
                        f"`{option.label}`" +
                        (
                            f"\n*({option.description})*"
                            if option.description
                            else ""
                        )
                        for option in self.options
                    ) if self.options else "`Not Set`",
                    inline=False
                )
            )

        return U.make_embed(
            title=f"__Application Question #{self._parent.questions.index(self) + 1}__",
            fields=fields
        )

################################################################################
    async def menu(self, interaction: Interaction) -> None:

        embed = self.status()
        view = FormQuestionStatusView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def set_component_type(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set UI Component Type__",
            description="Pick the UI component type for this question from the selector below."
        )
        view = FroggeSelectView(interaction.user, UIComponentType.select_options())

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.ui_type = UIComponentType(int(view.value))

################################################################################
    async def toggle_required(self, interaction: Interaction) -> None:

        self.required = not self.required
        await interaction.respond("** **", delete_after=0.1)

################################################################################
    async def set_primary_text(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Question Primary Text",
            attribute="Text",
            cur_val=self.primary_text,
            example="eg. 'What is the airspeed velocity of an unladen swallow?'",
            max_length=80
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.primary_text = modal.value

################################################################################
    async def set_secondary_text(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Question Secondary Text",
            attribute="Text",
            cur_val=self.secondary_text,
            example="eg. 'Please provide your answer in the form of a number.'",
            max_length=80,
            multiline=True
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.secondary_text = modal.value

################################################################################
    async def add_option(self, interaction: Interaction) -> None:

        assert self.ui_type in (UIComponentType.SelectMenu, UIComponentType.MultiSelect)

        if len(self.options) >= self.MAX_OPTIONS:
            error = MaxItemsReached("Option", self.MAX_OPTIONS)
            await interaction.respond(embed=error, ephemeral=True)
            return

        new_option = FormOption.new(self)
        self.options.append(new_option)

        await new_option.menu(interaction)

################################################################################
    async def modify_option(self, interaction: Interaction) -> None:

        assert self.ui_type in (UIComponentType.SelectMenu, UIComponentType.MultiSelect)

        prompt = U.make_embed(
            title="__Modify Option__",
            description="Pick an option from the list below to modify."
        )
        view = FroggeSelectView(interaction.user, self.select_options())

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        option = self.get_option(view.value)
        await option.menu(interaction)

################################################################################
    async def remove_option(self, interaction: Interaction) -> None:

        assert self.ui_type in (UIComponentType.SelectMenu, UIComponentType.MultiSelect)

        prompt = U.make_embed(
            title="__Remove Option__",
            description="Pick an option from the list below to remove."
        )
        view = FroggeSelectView(interaction.user, self.select_options())

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        option = self.get_option(view.value)
        await option.remove(interaction)

################################################################################
    def select_options(self) -> List[SelectOption]:

        return [
            SelectOption(
                label=option.label or "Unlabelled Question",
                value=str(option.id),
            )
            for option in self.options
        ]

################################################################################
    def get_option(self, option_id: str) -> Optional[FormOption]:

        return next((option for option in self.options if option.id == int(option_id)), None)

################################################################################
    async def remove(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Question__",
            description="Are you sure you want to remove this question?"
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.delete()

################################################################################
    def user_status(self, user: User) -> Embed:

        response = self._responses.get(user.id, [])
        response_str = "\n".join(f"`{r}`" for r in response) if response else "`Not Responded`"

        return U.make_embed(
            title=f"__{self.primary_text}__",
            description=(
                    (f"*{self.secondary_text}*" if self.secondary_text else "") +
                    "\n" +
                    ("***(Required)***" if self.required else "")
            ),
            fields=[
                EmbedField(
                    name="__Your Response__",
                    value=response_str,
                    inline=False
                )
            ]
        )

################################################################################
    def page(self, user: User) -> Page:

        return Page(
            embeds=[self.user_status(user)],
            custom_view=FormPageResponseView(self)
        )

################################################################################
    async def respond(self, interaction: Interaction) -> None:

        if self.pre_prompt.is_active and self.pre_prompt.is_filled_out:
            if not await self.pre_prompt.send(interaction):
                return

        match self.ui_type:
            case UIComponentType.ShortText:
                resp = await self._respond_to_short_text(interaction)
            case UIComponentType.LongText:
                resp = await self._respond_to_long_text(interaction)
            case UIComponentType.SelectMenu:
                resp = await self._respond_to_select_menu(interaction)
            case UIComponentType.MultiSelect:
                resp = await self._respond_to_multi_select(interaction)
            case _:
                raise NotImplementedError(f"UI Component Type {self.ui_type} is not implemented.")

        if resp is None:
            return

        user, response = resp
        if self.post_prompt.is_active and self.post_prompt.is_filled_out:
            if await self.post_prompt.send(interaction):
                self._insert_form_response(user, response)
        else:
            self._insert_form_response(user, response)

################################################################################
    def _insert_form_response(self, user: User, response: List[str]) -> None:

        self.bot.api.create_form_response(self.id, user.id, response)
        self._responses[user.id] = response

################################################################################
    async def _respond_to_short_text(self, interaction: Interaction) -> Optional[Tuple[User, List[str]]]:

        assert self.ui_type == UIComponentType.ShortText, f"Invalid UI Component Type: {self.ui_type.proper_name}"

        modal = BasicTextModal(
            title=self.primary_text,
            attribute="Response",
            max_length=200,
            required=self.required
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        return interaction.user, [modal.value]

################################################################################
    async def _respond_to_long_text(self, interaction: Interaction) -> Optional[Tuple[User, List[str]]]:

        assert self.ui_type == UIComponentType.LongText, f"Invalid UI Component Type: {self.ui_type.proper_name}"

        modal = BasicTextModal(
            title=self.primary_text,
            attribute="Response",
            max_length=500,
            required=self.required,
            multiline=True
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        return interaction.user, [modal.value]

################################################################################
    async def _respond_to_select_menu(self, interaction: Interaction) -> Optional[Tuple[User, List[str]]]:

        assert self.ui_type == UIComponentType.SelectMenu, f"Invalid UI Component Type: {self.ui_type.proper_name}"

        prompt = U.make_embed(
            title=self.primary_text,
            description=self.secondary_text if self.secondary_text else None
        )
        view = FroggeSelectView(
            owner=interaction.user,
            options=[o.select_option() for o in self.options]
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        response = self.get_option(view.value)
        return interaction.user, [response.value]

################################################################################
    async def _respond_to_multi_select(self, interaction: Interaction) -> Optional[Tuple[User, List[str]]]:

        assert self.ui_type == UIComponentType.MultiSelect, f"Invalid UI Component Type: {self.ui_type.proper_name}"

        prompt = U.make_embed(
            title=self.primary_text,
            description=self.secondary_text if self.secondary_text else None
        )
        view = FroggeSelectView(
            owner=interaction.user,
            options=[o.select_option() for o in self.options],
            multi_select=True
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        responses = [self.get_option(v).value for v in view.value]
        return interaction.user, responses

################################################################################
    def delete_response(self, user: User) -> None:

        if user.id in self._responses:
            self.bot.api.delete_form_response(self.id, user.id)
            del self._responses[user.id]

################################################################################
    def is_complete(self, user: User) -> bool:

        return user.id in self._responses

################################################################################
    async def prompt_menu(self, interaction) -> None:

        options = [
            SelectOption(
                label="Pre-Prompt",
                value="pre"
            ),
            SelectOption(
                label="Post-Prompt",
                value="post"
            )
        ]

        prompt = U.make_embed(
            title="__Select a Prompt to Edit__",
            description="Would you like to edit the Pre- or Post-Prompt for this question?"
        )
        view = FroggeSelectView(interaction.user, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        if view.value == "pre":
            await self.pre_prompt.menu(interaction)
        elif view.value == "post":
            await self.post_prompt.menu(interaction)

################################################################################
