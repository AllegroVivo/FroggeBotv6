from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any, Dict, Type, TypeVar

from discord import Embed, Interaction

from Errors import InvalidURL
from Assets import BotEmojis
from Utilities import Utilities as U
from UI.Embeds import EmbedHeaderStatusView
from UI.Common import BasicTextModal, ConfirmCancelView

if TYPE_CHECKING:
    from Classes import FroggeEmbed, FroggeBot
################################################################################

__all__ = ("FroggeEmbedHeader", )

FEH = TypeVar("FEH", bound="FroggeEmbedHeader")

################################################################################
class FroggeEmbedHeader:

    __slots__ = (
        "_parent",
        "_text",
        "_icon_url",
        "_url",
    )

################################################################################
    def __init__(self, parent: FroggeEmbed, **kwargs) -> None:

        self._parent: FroggeEmbed = parent

        self._text: Optional[str] = kwargs.get("text")
        self._icon_url: Optional[str] = kwargs.get("icon_url")
        self._url: Optional[str] = kwargs.get("url")

################################################################################
    @classmethod
    def load(cls: Type[FEH], parent: FroggeEmbed, data: Dict[str, Any]) -> FEH:

        return cls(
            parent=parent,
            text=data["text"],
            icon_url=data["icon_url"],
            url=data["url"]
        )

################################################################################
    @property
    def bot(self) -> FroggeBot:

        return self._parent.bot

################################################################################
    @property
    def parent_id(self) -> int:

        return self._parent.id

################################################################################
    @property
    def text(self) -> Optional[str]:

        return self._text

    @text.setter
    def text(self, value: Optional[str]) -> None:

        self._text = value
        self.update()

################################################################################
    @property
    def icon_url(self) -> Optional[str]:

        return self._icon_url

    @icon_url.setter
    def icon_url(self, value: Optional[str]) -> None:

        self._icon_url = value
        self.update()

################################################################################
    @property
    def url(self) -> Optional[str]:

        return self._url

    @url.setter
    def url(self, value: Optional[str]) -> None:

        self._url = value
        self.update()

################################################################################
    def update(self) -> None:

        self.bot.api.update_embed_header(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "text": self.text,
            "icon_url": self.icon_url,
            "url": self.url
        }

################################################################################
    def status(self) -> Embed:

        description = (
            "**Header Text:**\n"
            f"{self.text or '`Not Set`'}\n\n"
            
            f"**Header URL:**\n"
            f"{self.url or '`Not Set`'}\n\n"

            "**Header Icon:**\n"
        )
        if self.icon_url is None:
            description += "`Not Set`"
        else:
            description += f"{BotEmojis.ArrowRight}{BotEmojis.ArrowRight}{BotEmojis.ArrowRight}"

        return U.make_embed(
            title="__Embed Header Status__",
            description=description,
            thumbnail_url=self.icon_url
        )

################################################################################
    async def menu(self, interaction: Interaction) -> None:

        embed = self.status()
        view = EmbedHeaderStatusView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def set_text(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Header Text",
            attribute="Text",
            cur_val=self.text,
            max_length=250,
            required=False
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.text = modal.value

################################################################################
    async def set_url(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Header URL",
            attribute="URL",
            cur_val=self.url,
            max_length=500,
            required=False
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        if not modal.value.startswith("http://") and not modal.value.startswith("https://"):
            error = InvalidURL(modal.value)
            await interaction.respond(embed=error, ephemeral=True)
            return

        self.url = modal.value

################################################################################
    async def set_icon(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Header Icon__",
            description="Please provide an image for the embed's header icon."
        )
        image_url = await U.wait_for_image(interaction, prompt)
        if image_url is not None:
            self.icon_url = image_url

################################################################################
    async def remove_icon(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Header Icon__",
            description="Are you sure you want to remove the header icon?"
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.icon_url = None

################################################################################
