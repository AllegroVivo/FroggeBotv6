from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any, Dict, TypeVar, Type

from discord import Embed, Interaction

from Assets import BotEmojis
from Utilities import Utilities as U
from UI.Embeds import EmbedFooterStatusView
from UI.Common import BasicTextModal, ConfirmCancelView

if TYPE_CHECKING:
    from Classes import FroggeEmbed, FroggeBot
################################################################################

__all__ = ("FroggeEmbedFooter", )

FEF = TypeVar("FEF", bound="FroggeEmbedFooter")

################################################################################
class FroggeEmbedFooter:

    __slots__ = (
        "_parent",
        "_icon_url",
        "_text",
    )

################################################################################
    def __init__(self, parent: FroggeEmbed, **kwargs) -> None:

        self._parent: FroggeEmbed = parent

        self._icon_url: Optional[str] = kwargs.get("icon_url")
        self._text: Optional[str] = kwargs.get("text")

################################################################################
    @classmethod
    def load(cls: Type[FEF], parent: FroggeEmbed, data: Dict[str, Any]) -> FEF:

        return cls(
            parent=parent,
            icon_url=data["icon_url"],
            text=data["text"]
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
    def icon_url(self) -> Optional[str]:

        return self._icon_url

    @icon_url.setter
    def icon_url(self, value: Optional[str]) -> None:

        self._icon_url = value
        self.update()

################################################################################
    @property
    def text(self) -> Optional[str]:

        return self._text

    @text.setter
    def text(self, value: Optional[str]) -> None:

        self._text = value
        self.update()

################################################################################
    def update(self) -> None:

        self.bot.api.update_embed_footer(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "icon_url": self.icon_url,
            "text": self.text
        }

################################################################################
    def status(self) -> Embed:

        description = (
            "**Footer Text:**\n"
            f"{self.text or '`Not Set`'}\n\n"
            
            "**Footer Icon:**\n"
        )
        if self.icon_url is None:
            description += "`Not Set`"
        else:
            description += f"{BotEmojis.ArrowRight}{BotEmojis.ArrowRight}{BotEmojis.ArrowRight}"

        return U.make_embed(
            title="__Footer Status__",
            description=description,
            thumbnail_url=self.icon_url,
        )

################################################################################
    async def menu(self, interaction: Interaction) -> None:

        embed = self.status()
        view = EmbedFooterStatusView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def set_text(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Footer Text",
            attribute="Text",
            cur_val=self.text,
            max_length=2000,
            required=False,
            multiline=True
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.text = modal.value

################################################################################
    async def set_icon(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Footer Icon__",
            description=(
                "Please provide the image you would like to set as the footer icon."
            )
        )
        icon_url = await U.wait_for_image(interaction, prompt)
        if icon_url is not None:
            self.icon_url = icon_url

################################################################################
    async def remove_icon(self, interaction: Interaction) -> None:

        confirmation = U.make_embed(
            title="__Remove Footer Icon__",
            description=(
                "Are you sure you want to remove the footer icon?"
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=confirmation, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.icon_url = None

################################################################################
