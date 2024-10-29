from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar, Any, Dict

from Classes.Common import LazyChannel
from discord import PartialEmoji, Embed, EmbedField, Interaction, TextChannel, ChannelType
from Utilities import Utilities as U, FroggeColor
from Assets import BotEmojis
from UI.Forms import FormPostOptionsStatusView
from UI.Common import BasicTextModal, AccentColorModal, ConfirmCancelView

if TYPE_CHECKING:
    from Classes import Form, FroggeBot, GuildData
################################################################################

__all__ = ("FormPostOptions", )

FPO = TypeVar("FPO", bound="FormPostOptions")

################################################################################
class FormPostOptions:

    __slots__ = (
        "_parent",
        "_description",
        "_thumbnail",
        "_button_label",
        "_button_emoji",
        "_color",
        "_channel",
    )

################################################################################
    def __init__(self, parent: Form, **kwargs) -> None:

        self._parent: Form = parent

        self._description: Optional[str] = kwargs.get("description")
        self._thumbnail: Optional[str] = kwargs.get("thumbnail")
        self._button_label: Optional[str] = kwargs.get("button_label")
        self._button_emoji: Optional[PartialEmoji] = kwargs.get("button_emoji")
        self._color: Optional[FroggeColor] = kwargs.get("color")
        self._channel: LazyChannel = LazyChannel(self, kwargs.get("channel_id"))

################################################################################
    @classmethod
    def load(cls: Type[FPO], parent: Form, data: Dict[str, Any]) -> FPO:

        return cls(
            parent=parent,
            description=data.get("description"),
            thumbnail=data.get("thumbnail_url"),
            button_label=data.get("button_label"),
            button_emoji=PartialEmoji.from_str(data.get("button_emoji")) if data.get("button_emoji") else None,
            color=FroggeColor(data.get("color")) if data.get("color") else None,
            channel_id=data.get("channel_id")
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
    def description(self) -> Optional[str]:

        return self._description

    @description.setter
    def description(self, value: Optional[str]) -> None:

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
    def button_label(self) -> Optional[str]:

        return self._button_label

    @button_label.setter
    def button_label(self, value: Optional[str]) -> None:

        self._button_label = value
        self.update()

################################################################################
    @property
    def button_emoji(self) -> Optional[PartialEmoji]:

        return self._button_emoji

    @button_emoji.setter
    def button_emoji(self, value: Optional[PartialEmoji]) -> None:

        self._button_emoji = value
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
    async def post_channel(self) -> Optional[TextChannel]:

        return await self._channel.get()

    @post_channel.setter
    def post_channel(self, value: Optional[TextChannel]) -> None:

        self._channel.set(value)

################################################################################
    def update(self) -> None:

        self.bot.api.update_form_post_options(self)

################################################################################
    def to_dict(self) -> dict:

        return {
            "description": self.description,
            "thumbnail_url": self.thumbnail,
            "button_label": self.button_label,
            "button_emoji": self.button_emoji,
            "color": self.color.value if self.color is not None else None,
            "channel_id": self._channel.id
        }

################################################################################
    async def status(self) -> Embed:

        channel = await self.post_channel
        return U.make_embed(
            title=f"__Form Post Options for {self._parent.name or 'Unnamed Form'}__",
            description=(
                f"**Post Description:**\n"
                f"```{self.description}```"
            ),
            thumbnail_url=self.thumbnail,
            fields=[
                EmbedField(
                    name="__Post Channel__",
                    value=(
                        channel.mention
                        if channel is not None
                        else "`Not Set`"
                    ),
                    inline=False
                ),
                EmbedField(
                    name="__Accent Color__",
                    value=(
                        f"{BotEmojis.ArrowLeft} -- (__{str(self.color).upper()}__)"
                        if self._color is not None
                        else "`Not Set`"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__Button Label__",
                    value=f"`{self.button_label or 'Not Set'}`",
                    inline=True
                ),
                EmbedField(
                    name="__Button Emoji__",
                    value=(
                        str(self.button_emoji)
                        if self.button_emoji is not None
                        else "`Not Set`"
                    ),
                    inline=True
                )
            ]
        )

################################################################################
    def compile(self) -> Embed:

        return U.make_embed(
            color=self.color or FroggeColor.embed_background(),
            title=self._parent.name or "Unnamed Form",
            description=self.description,
            thumbnail_url=self.thumbnail
        )

################################################################################
    async def menu(self, interaction: Interaction) -> None:

        embed = await self.status()
        view = FormPostOptionsStatusView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def set_description(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Form Post Description",
            attribute="Description",
            cur_val=self.description,
            max_length=500,
            required=False,
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
            title="Set Form Post Thumbnail",
            description=(
                "Please upload an image for the thumbnail you would like to "
                "use for this form post."
            )
        )
        image_url = await U.wait_for_image(interaction, prompt)
        if image_url is not None:
            self.thumbnail = image_url

################################################################################
    async def set_button_label(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Form Post Button Label",
            attribute="Label",
            cur_val=self.button_label,
            max_length=80,
            required=False
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.button_label = modal.value

################################################################################
    async def set_button_emoji(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="Set Form Post Button Emoji",
            description=(
                "Please send the emoji you would like to use for the button "
                "on this form post."
            )
        )
        emoji = await U.listen_for(interaction, prompt, U.MentionableType.Emoji)
        if emoji is not None:
            self.button_emoji = emoji

################################################################################
    async def set_channel(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="Set Form Post Channel",
            description=(
                "Please select the channel you would like to use for this form post."
            )
        )
        channel = await U.select_channel(interaction, self.guild, "Form Post Channel", prompt)
        if channel is not None:
            self.post_channel = channel

################################################################################
    async def set_color(self, interaction: Interaction) -> None:

        modal = AccentColorModal(self.color)

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.color = modal.value

################################################################################
    async def remove_thumbnail(self, interaction: Interaction) -> None:

        confirm = U.make_embed(
            title="Remove Thumbnail",
            description=(
                "Are you sure you want to remove the thumbnail from this form post?"
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.thumbnail = None

################################################################################
    async def remove_emoji(self, interaction: Interaction) -> None:

        self.button_emoji = None
        await interaction.respond("** **", delete_after=0.1)

################################################################################
