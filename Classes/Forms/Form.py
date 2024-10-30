from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List, Dict, Any, Type, TypeVar, Union

from discord import (
    User,
    Embed,
    TextChannel,
    Role,
    CategoryChannel,
    Interaction,
    SelectOption,
    Message,
    NotFound,
)
from discord.ext.pages import Page

from Assets import BotEmojis
from Classes.Common import ManagedObject, LazyUser, LazyRole, LazyChannel, LazyMessage
from Enums import DisplayTime
from Errors import MaxItemsReached, ChannelNotSet
from UI.Common import BasicTextModal, FroggeSelectView, Frogginator
from UI.Forms import (
    FormStatusView,
    FormPromptsMenuView,
    FormNotificationsManagerView,
    FormChannelStatusView,
    FormPostView,
)
from Utilities import Utilities as U
from .FormNotificationsManager import FormNotificationsManager
from .FormPostOptions import FormPostOptions
from .FormPrompt import FormPrompt
from .FormQuestion import FormQuestion
from .FormResponseCollection import FormResponseCollection

if TYPE_CHECKING:
    from Classes import FormsManager
    from UI.Common import FroggeView
################################################################################

__all__ = ("Form", )

F = TypeVar("F", bound="Form")

################################################################################
class Form(ManagedObject):

    __slots__ = (
        "_questions",
        "_responses",
        "_channel",
        "_name",
        "_pre_prompt",
        "_post_prompt",
        "_notifications",
        "_create_channel",
        "_channel_roles",
        "_category",
        "_post_options",
        "_post_msg",
    )

    MAX_QUESTIONS = 20
    MAX_TO_NOTIFY = 10

################################################################################
    def __init__(self, mgr: FormsManager, _id: int, **kwargs) -> None:

        super().__init__(mgr, _id)

        self._name: str = kwargs.get("name")
        self._channel: LazyChannel = LazyChannel(self, kwargs.get("log_channel_id"))

        self._questions: List[FormQuestion] = kwargs.get("questions", [])
        self._responses: List[FormResponseCollection] = kwargs.get("responses", [])

        self._pre_prompt: FormPrompt = kwargs.pop("pre_prompt")
        self._post_prompt: FormPrompt = kwargs.pop("post_prompt")

        self._notifications: FormNotificationsManager = (
            kwargs.get("notifications", FormNotificationsManager(self))
        )
        self._create_channel: bool = kwargs.get("create_channel", False)
        self._channel_roles: List[LazyRole] = kwargs.get("channel_roles", [])
        self._category: LazyChannel = LazyChannel(self, kwargs.get("category_id"))

        self._post_options: FormPostOptions = FormPostOptions(self)
        self._post_msg: LazyMessage = LazyMessage(self, kwargs.get("post_url"))

################################################################################
    @classmethod
    def new(cls: Type[F], mgr: FormsManager, name: str) -> F:

        form_data = mgr.bot.api.create_form(mgr.guild_id, name)

        pre_prompt = post_prompt = None
        for prompt in form_data["prompts"]:
            if prompt["prompt_type"] == 1:
                pre_prompt = FormPrompt.load(cls, DisplayTime.Before, prompt)
            elif prompt["prompt_type"] == 2:
                post_prompt = FormPrompt.load(cls, DisplayTime.After, prompt)

        assert pre_prompt is not None and post_prompt is not None
        return cls(mgr, form_data["id"], name=name, pre_prompt=pre_prompt, post_prompt=post_prompt)

################################################################################
    @classmethod
    def load(cls: Type[F], mgr: FormsManager, data: Dict[str, Any]) -> F:

        self: F = cls.__new__(cls)

        self._id = data["id"]
        self._mgr = mgr

        self._name = data["form_name"]
        self._channel = LazyChannel(self, data["log_channel_id"])

        self._questions = [FormQuestion.load(self, q) for q in data["questions"]]
        self._responses = [FormResponseCollection.load(self, r) for r in data["response_collections"]]

        for prompt in data["prompts"]:
            if prompt["prompt_type"] == 1:
                self._pre_prompt = FormPrompt.load(self, DisplayTime.Before, prompt)
            elif prompt["prompt_type"] == 2:
                self._post_prompt = FormPrompt.load(self, DisplayTime.After, prompt)

        self._notifications = FormNotificationsManager.load(self, data["notify_roles"], data["notify_users"])
        self._create_channel = data["create_channel"]
        self._channel_roles = [LazyRole(self, r) for r in data["channel_roles"]]
        self._category = LazyChannel(self, data["creation_category_id"])

        self._post_options = FormPostOptions.load(self, data["post_options"])
        self._post_msg = LazyMessage(self, data["post_url"])

        return self

################################################################################
    def __getitem__(self, question_id: int) -> Optional[FormQuestion]:

        return next((q for q in self._questions if q.id == int(question_id)), None)

################################################################################
    @property
    def name(self) -> str:

        return self._name

    @name.setter
    def name(self, value: str) -> None:

        self._name = value
        self.update()

################################################################################
    @property
    def questions(self) -> List[FormQuestion]:

        self._questions.sort(key=lambda q: q.order)
        return self._questions

################################################################################
    @property
    def responses(self) -> List[Any]:

        return self._responses

################################################################################
    @property
    async def channel(self) -> Optional[TextChannel]:

        return await self._channel.get()

    @channel.setter
    def channel(self, value: int) -> None:

        self._channel.set(value)

################################################################################
    @property
    async def post_message(self) -> Optional[Message]:

        return await self._post_msg.get()

    @post_message.setter
    def post_message(self, value: Optional[Message]) -> None:

        self._post_msg.set(value)

################################################################################
    @property
    def pre_prompt(self) -> FormPrompt:

        return self._pre_prompt

################################################################################
    @property
    def post_prompt(self) -> FormPrompt:

        return self._post_prompt

################################################################################
    @property
    def create_channel(self) -> bool:

        return self._create_channel

    @create_channel.setter
    def create_channel(self, value: bool) -> None:

        self._create_channel = value
        self.update()

################################################################################
    @property
    async def channel_roles(self) -> List[Role]:

        return [await r.get() for r in self._channel_roles]

################################################################################
    @property
    async def category(self) -> Optional[CategoryChannel]:

        return await self._category.get()

    @category.setter
    def category(self, value: int) -> None:

        self._category.set(value)

################################################################################
    @property
    def post_options(self) -> FormPostOptions:

        return self._post_options

################################################################################
    def update(self) -> None:

        self.bot.api.update_form(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "log_channel_id": self._channel.id,
            "form_name": self._name,
            "create_channel": self._create_channel,
            "channel_roles": [r.id for r in self._channel_roles],
            "creation_category_id": self._category.id,
            "post_url": self._post_msg.id,
            "notify_roles": [r.id for r in self._notifications._roles],
            "notify_users": [u.id for u in self._notifications._users],
        }

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_form(self.id)
        self._mgr._managed.remove(self)

################################################################################
    def select_option(self) -> SelectOption:

        return SelectOption(
            label=self.name,
            value=str(self.id)
        )

################################################################################
    async def status(self) -> Embed:

        log_channel = await self.channel
        desc = (
            f"**Questions:** [{len(self._questions)}]\n"
            f"**Form Log Channel:** "
            f"{log_channel.mention if log_channel else '`Not Set`'}\n"
            f"**Create Channel Upon Submission:** "
            f"{str(BotEmojis.CheckGreen if self.create_channel else BotEmojis.Cross)}\n\n"
        )
        if self.create_channel:
            cat = await self.category
            desc += (
                "__**Creation Category**__\n"
                f"{cat.mention if cat else '`Not Set`'}\n\n"

                "__**Roles With Access to Created Channel**__\n" +
                ("\n".join(
                    f"* {r.mention}"
                    for r in await self.channel_roles
                ) if self._channel_roles else "`Not Set`") + "\n\n"
            )

        desc += "__**Parties to Notify Upon Submission**__\n"

        roles = await self._notifications.roles
        users = await self._notifications.users
        for role in roles:
            desc += f"* {role.mention}\n"
        for user in users:
            desc += f"* {user.mention} ({user.display_name})\n"

        if not roles and not users:
            desc += "`None Set`\n"

        desc += "\nPress a button below to modify the form."

        return U.make_embed(
            title=f"__Form Status for: `{self.name}`__",
            description=desc,
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return FormStatusView(user, self)

################################################################################
    async def add_question(self, interaction: Interaction) -> None:

        if len(self._questions) >= self.MAX_QUESTIONS:
            error = MaxItemsReached("Question", self.MAX_QUESTIONS)
            await interaction.respond(embed=error, ephemeral=True)
            return

        modal = BasicTextModal(
            title="Enter Question Text",
            attribute="Value",
            example="eg. 'What is the airspeed velocity of an unladen swallow?'",
            max_length=80,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        question = FormQuestion.new(self)
        self._questions.append(question)

        question.primary_text = modal.value
        await question.menu(interaction)

################################################################################
    async def modify_question(self, interaction: Interaction) -> None:

        options = [
            SelectOption(
                label=question.primary_text or "No Text",
                value=str(question.id)
            )
            for question in self.questions
        ]

        prompt = U.make_embed(
            title="__Modify Question__",
            description="Pick a question from the list below to modify."
        )
        view = FroggeSelectView(interaction.user, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        question = self[view.value]
        await question.menu(interaction)

################################################################################
    async def remove_question(self, interaction: Interaction) -> None:

        options = [
            SelectOption(
                label=question.primary_text or "No Text",
                value=str(question.id)
            )
            for question in self.questions
        ]

        prompt = U.make_embed(
            title="__Remove Question__",
            description="Pick a question from the list below to remove."
        )
        view = FroggeSelectView(interaction.user, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        question = self[view.value]
        await question.remove(interaction)

################################################################################
    async def set_channel(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Form Log Channel__",
            description="Select the channel where form responses should be logged."
        )
        channel = await U.select_channel(interaction, self.guild, "Form Log Channel", prompt)
        if channel is None:
            return

        self.channel = channel

################################################################################
    async def prompts_menu(self, interaction: Interaction) -> None:

        embed = self.prompts_status()
        view = FormPromptsMenuView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    def prompts_status(self) -> Embed:

        return U.make_embed(
            title=f"__Form Prompt Status for: `{self.name}`__",
            description=(
                f"**[`Pre-Prompt Active`]:** "
                f"{BotEmojis.CheckGreen if self.pre_prompt.is_active else BotEmojis.Cross}\n"
                f"**[`Post-Prompt Active`]:** "
                f"{BotEmojis.CheckGreen if self.post_prompt.is_active else BotEmojis.Cross}\n\n"
            ),
        )

################################################################################
    async def pre_prompt_menu(self, interaction: Interaction) -> None:

        await self._pre_prompt.menu(interaction)

################################################################################
    async def post_prompt_menu(self, interaction: Interaction) -> None:

        await self._post_prompt.menu(interaction)

################################################################################
    async def toggle_create_channel(self, interaction: Interaction) -> None:

        self.create_channel = not self.create_channel
        await interaction.respond("** **", delete_after=0.1)

################################################################################
    async def notifications_menu(self, interaction: Interaction) -> None:

        await self._notifications.menu(interaction)

################################################################################
    async def _create_form_channel(self, user: User, response: FormResponseCollection, mention_str: str) -> None:

        guild = self._mgr.guild.parent
        member = await self._mgr.guild.get_or_fetch_member(user.id)

        if self._category is not None:
            cat_channel = await self.category
            channel = await cat_channel.create_text_channel(member.display_name)
        else:
            channel = await guild.create_text_channel(member.display_name)

        await channel.set_permissions(guild.default_role, view_channel=False)
        await channel.set_permissions(member, view_channel=True)
        for role in await self.channel_roles:
            await channel.set_permissions(role, view_channel=True)

        await channel.send(content=mention_str, embed=await response.compile())

################################################################################
    async def channel_status(self) -> Embed:

        cat_channel = await self.category
        return U.make_embed(
            title=f"__Channel Roles for: `{self.name}`__",
            description=(
                "__**Creation Category**__\n"
                f"{cat_channel.mention if cat_channel else '`Not Set`'}\n\n"

                "__**Roles With Access to Created Channel**__\n" +
                (
                    "\n".join(
                        f"* {r.mention} ({r.name})"
                        for r in await self.channel_roles
                    )
                    if await self.channel_roles else "`Not Set`"
                )
            )
        )

################################################################################
    async def manage_channel(self, interaction: Interaction) -> None:

        embed = await self.channel_status()
        view = FormChannelStatusView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def add_channel_role(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Add Channel Role__",
            description="Mention the role you want to have access to the created channel."
        )
        role = await U.listen_for(interaction, prompt, U.MentionableType.Role)
        if role is None:
            return

        self._channel_roles.append(LazyRole(self, role.id))
        self.update()

################################################################################
    async def remove_channel_role(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Channel Role__",
            description="Mention the role you want to remove from the channel roles list."
        )
        role = await U.listen_for(interaction, prompt, U.MentionableType.Role)
        if role is None:
            return

        if role not in [r.id for r in self._channel_roles]:
            await interaction.respond("Role is not in the channel roles list.")
            return

        for r in self._channel_roles:
            if r.id == role.id:
                self._channel_roles.remove(r)
        self.update()

################################################################################
    async def set_category(self, interaction: Interaction) -> None:

        options = [
            SelectOption(
                label=cat.name,
                value=str(cat.id)
            )
            for cat in self._mgr.guild.parent.categories
        ]

        prompt = U.make_embed(
            title="__Set Creation Category__",
            description="Please select the category where created channels should be placed."
        )
        view = FroggeSelectView(interaction.user, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.category = self.bot.get_channel(int(view.value))

################################################################################
    async def post_options_menu(self, interaction: Interaction) -> None:

        await self._post_options.menu(interaction)

################################################################################
    async def post(self, interaction: Interaction) -> None:

        post_channel = await self.post_options.post_channel
        if post_channel is None:
            error = ChannelNotSet("Form Post Channel")
            await interaction.respond(embed=error, ephemeral=True)
            return

        if await self.update_post_components():
            return

        view = FormPostView(self)
        self.bot.add_view(view)

        self.post_message = await post_channel.send(embed=self.post_options.compile(), view=view)

        success = U.make_embed(
            title="__Form Posted__",
            description=f"Form has been posted to {post_channel.mention}."
        )
        await interaction.respond(embed=success)

################################################################################
    async def update_post_components(self) -> bool:

        post_message = await self.post_message
        if post_message is None:
            return False

        view = FormPostView(self)
        self.bot.add_view(view)

        try:
            await post_message.edit(embed=self.post_options.compile(), view=view)
        except NotFound:
            self.post_message = None
            return False
        else:
            return True

################################################################################
    async def fill_out(self, interaction: Interaction) -> None:

        if self.pre_prompt.is_active and self.pre_prompt.is_filled_out:
            if not await self.pre_prompt.send(interaction):
                return

        pages = [
            q.page(interaction.user)
            for q
            in self.questions
        ]
        frogginator = Frogginator(pages, self)
        await frogginator.respond(interaction)  # , ephemeral=True)

################################################################################
    def is_complete(self, user: User) -> bool:

        for q in self.questions:
            if q.required and not q.is_complete(user):
                return False

        return True

################################################################################
    async def submit(self, interaction: Interaction) -> bool:

        log_channel = await self.channel
        if log_channel is None:
            error = ChannelNotSet("Form Response Log Channel")
            await interaction.respond(embed=error, ephemeral=True)
            return False

        if not self.is_complete(interaction.user):
            qlist = [
                q.order
                for q in self.questions
                if not q.is_complete(interaction.user)
                and q.required
            ]
            error = U.make_error(
                title="Form Incomplete",
                description=(
                    "__Required Questions:__\n"
                    + ", ".join(f"#{q}" for q in qlist)
                ),
                message="One or more required questions have not been answered.",
                solution="Please answer all required questions before submitting your form."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return False

        if self.post_prompt.is_active and self.post_prompt.is_filled_out:
            if not await self.post_prompt.send(interaction):
                return False

        inter = await interaction.respond("Processing application... Please wait...")

        questions = [q.primary_text for q in self.questions]
        responses = [
            "\n".join(q[interaction.user.id])
            if q[interaction.user.id]
            else "`No Response`"
            for q in self.questions
        ]

        new_collection = FormResponseCollection.new(
            self, interaction.user, questions, responses
        )
        self._responses.append(new_collection)

        for q in self.questions:
            q.delete_response(interaction.user)

        roles = await self._notifications.roles
        role_str = ", ".join(r.mention for r in roles)

        try:
            await inter.delete()
        except:
            try:
                await inter.delete_original_response()
            except:
                pass

        msg = await log_channel.send(content=role_str, embed=await new_collection.compile())

        user_str = ""
        users = await self._notifications.users
        if users:
            confirm = U.make_embed(
                title="__Form Submitted__",
                description=(
                    f"A form has been successfully submitted.\n"
                    f"**Form Name:** `{self.name or 'Unnamed Form'}`\n\n"

                    f"You can view the form response here: {msg.jump_url}"
                )
            )

            for user in users:
                try:
                    await user.send(embed=confirm)
                except:
                    pass
                user_str += f"{user.mention} "

        if self.create_channel:
            await self._create_form_channel(interaction.user, new_collection, role_str + user_str)

        return True

################################################################################
    async def paginate_responses(self, interaction: Interaction) -> None:

        pages = [
            Page(embeds=[await response.compile()])
            for response
            in self._responses
        ]
        frogginator = Frogginator(pages, self)
        await frogginator.respond(interaction)

################################################################################
    async def remove(self, interaction: Interaction) -> None:

        await super().remove(interaction)

        post_message = await self.post_message
        if post_message is not None:
            try:
                await post_message.delete()
            except:
                pass

################################################################################
