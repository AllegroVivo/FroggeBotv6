from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any, Dict, Type, TypeVar

from Assets import BotImages, BotEmojis
from discord import Embed, EmbedField, Interaction

from UI.Common import ConfirmCancelView
from Utilities import Utilities as U
from UI.Embeds import EmbedImagesStatusView

if TYPE_CHECKING:
    from Classes import FroggeEmbed, FroggeBot
################################################################################

__all__ = ("FroggeEmbedImages",)

FEI = TypeVar("FEI", bound="FroggeEmbedImages")

################################################################################
class FroggeEmbedImages:

    __slots__ = (
        "_parent",
        "_thumbnail",
        "_main_image",
    )

################################################################################
    def __init__(self, parent: FroggeEmbed, **kwargs) -> None:

        self._parent: FroggeEmbed = parent

        self._thumbnail: Optional[str] = kwargs.get("thumbnail")
        self._main_image: Optional[str] = kwargs.get("main_image")

################################################################################
    @classmethod
    def load(cls: Type[FEI], parent: FroggeEmbed, data: Dict[str, Any]) -> FEI:

        return cls(
            parent=parent,
            thumbnail=data["thumbnail"],
            main_image=data["main_image"]
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
    def thumbnail(self) -> Optional[str]:

        return self._thumbnail

    @thumbnail.setter
    def thumbnail(self, value: Optional[str]) -> None:

        self._thumbnail = value
        self.update()

################################################################################
    @property
    def main_image(self) -> Optional[str]:

        return self._main_image

    @main_image.setter
    def main_image(self, value: Optional[str]) -> None:

        self._main_image = value
        self.update()

################################################################################
    def update(self) -> None:

        self.bot.api.update_embed_images(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "thumbnail": self._thumbnail,
            "main_image": self._main_image,
        }

################################################################################
    def status(self) -> Embed:

        return U.make_embed(
            title="Embed Images",
            fields=[
                EmbedField(
                    name="__Main Image__",
                    value=(
                        f"{BotEmojis.ArrowDown}{BotEmojis.ArrowDown}{BotEmojis.ArrowDown}\n"
                        if self.main_image
                        else "`Not Set`"
                    )
                ),
                EmbedField(
                    name="__Thumbnail Image__",
                    value=(
                        f"{BotEmojis.ArrowRight}{BotEmojis.ArrowRight}{BotEmojis.ArrowRight}\n"
                        if self.thumbnail
                        else "`Not Set`"
                    )
                ),
            ],
            thumbnail_url=self.thumbnail or BotImages.ThumbnailMissing,
            image_url=self.main_image or BotImages.MainImageMissing
        )

################################################################################
    async def menu(self, interaction: Interaction) -> None:

        embed = self.status()
        view = EmbedImagesStatusView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def set_thumbnail(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="Set Thumbnail",
            description="Please upload the image for the thumbnail you'd like to set."
        )
        image_url = await U.wait_for_image(interaction, prompt)
        if image_url is not None:

            self.thumbnail = image_url

################################################################################
    async def remove_thumbnail(self, interaction: Interaction) -> None:

        confirm = U.make_embed(
            title="Remove Thumbnail",
            description="Are you sure you want to remove the thumbnail?"
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.thumbnail = None

################################################################################
    async def set_main_image(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="Set Main Image",
            description="Please upload the image for the main image you'd like to set."
        )
        image_url = await U.wait_for_image(interaction, prompt)
        if image_url is not None:

            self.main_image = image_url

################################################################################
    async def remove_main_image(self, interaction: Interaction) -> None:

        confirm = U.make_embed(
            title="Remove Main Image",
            description="Are you sure you want to remove the main image?"
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.main_image = None

################################################################################
