from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List, Type, TypeVar, Any, Tuple, Dict

from discord import Interaction, Embed, EmbedField

from Utilities import Utilities as U
from UI.Common import ConfirmCancelView
from UI.Profiles import (
    ProfileImagesStatusView,
    ProfileThumbnailStatusView,
    ProfileMainImageStatusView,
    AdditionalImageFrogginator
)
from .AdditionalImage import AdditionalImage
from .ProfileSection import ProfileSection
from Assets import BotEmojis, BotImages
from Utilities.Constants import MAX_ADDITIONAL_IMAGES

if TYPE_CHECKING:
    from Classes import Profile
################################################################################

__all__ = ("ProfileImages", )

PI = TypeVar("PI", bound="ProfileImages")

################################################################################
class ProfileImages(ProfileSection):

    __slots__ = (
        "_thumbnail",
        "_main_image",
        "_additional",
    )
    
################################################################################
    def __init__(self, parent: Profile, **kwargs) -> None:

        super().__init__(parent)
        
        self._thumbnail: Optional[str] = kwargs.get("thumbnail")
        self._main_image: Optional[str] = kwargs.get("main_image")
        self._additional: List[AdditionalImage] = kwargs.get("additional", None) or []
    
################################################################################
    @classmethod
    def load(cls: Type[PI], parent: Profile, data: Dict[str, Any]) -> PI:
        
        self: PI = cls.__new__(cls)
        self._parent = parent
        
        self._thumbnail = data["thumbnail_url"]
        self._main_image = data["main_image_url"]
        self._additional = [AdditionalImage.load(self, a) for a in data["additional"]]
        
        return self
    
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
    @property
    def additional(self) -> List[AdditionalImage]:
        
        return self._additional
    
################################################################################
    def get_additional(self, image_id: str) -> Optional[AdditionalImage]:
        
        return next((a for a in self.additional if a.id == image_id), None)
            
################################################################################
    def update(self) -> None:
        
        self.bot.api.update_profile_images(self)
        
################################################################################
    def to_dict(self) -> dict:
        
        return {
            "thumbnail_url": self._thumbnail,
            "main_image_url": self._main_image,
        }
    
################################################################################
    async def menu(self, interaction: Interaction) -> None:

        embed = self.status()
        view = ProfileImagesStatusView(interaction.user, self)

        await interaction.response.send_message(embed=embed, view=view)
        await view.wait()
        
################################################################################
    def status(self) -> Embed:

        down_arrow = str(BotEmojis.ArrowDown)
        right_arrow = str(BotEmojis.ArrowRight)

        fields: List[EmbedField] = [
            EmbedField(U.draw_line(extra=30), "** **", False),
            self.additional_status(),
            EmbedField(U.draw_line(extra=30), "** **", False),
            EmbedField(
                name="__Main Image__",
                value=f"-{down_arrow}{down_arrow}{down_arrow}-",
                inline=True
            ),
            EmbedField("** **", "** **", True),
            EmbedField(
                name="__Thumbnail__",
                value=f"-{right_arrow}{right_arrow}{right_arrow}-",
                inline=True
            ),
        ]

        return U.make_embed(
            color=self.parent.color,
            title=f"Image Details for `{self.parent.name}`",
            description=(
                "The buttons below allow you to remove and image attached to your profile "
                "or to view a paginated list of your current additional images.\n\n"

                "***To change your thumbnail and main image assets, or to add an additional image\n"
                "to your profile, click one of the buttons below!***"
            ),
            thumbnail_url=self._thumbnail or BotImages.ThumbnailMissing,
            image_url=self._main_image or BotImages.MainImageMissing,
            timestamp=False,
            fields=fields
        )
    
################################################################################
    def compile(self) -> Tuple[Optional[str], Optional[str], Optional[EmbedField]]:

        return (
            self.thumbnail,
            self.main_image,
            self.compile_additional()
        )
    
################################################################################
    def progress(self) -> str:

        em_thumb = self.progress_emoji(self._thumbnail)
        em_main = self.progress_emoji(self._main_image)
        em_addl = self.progress_emoji(self.additional)
    
        return (
            f"{U.draw_line(extra=15)}\n"
            "__**Images**__\n"
            f"{em_thumb} -- Thumbnail *(Upper-Right)*\n"
            f"{em_main} -- Main Image *(Bottom-Center)*\n"
            f"{em_addl} -- (`{len(self.additional)}`) -- Additional Images\n"
        )
    
################################################################################
    def additional_status(self) -> EmbedField:

        if not self.additional:
            return EmbedField(
                name="__Additional Images__",
                value="`Not Set`",
                inline=False
            )

        return self.compile_additional()

################################################################################
    def compile_additional(self) -> Optional[EmbedField]:

        if not self.additional:
            return

        images_text = ""
        for image in self.additional:
            images_text += f"{image.compile()}\n"

        return EmbedField(
            name=f"{BotEmojis.Camera} __Additional Images__ {BotEmojis.Camera}",
            value=images_text,
            inline=False
        )

################################################################################
    def thumbnail_status(self) -> Embed:
        
        return U.make_embed(
            title="__Thumbnail Image__",
            description=(
                "This image is displayed in the upper-right corner of your profile.\n"
                "To change this image, use the buttons below."
            ),
            thumbnail_url=self._thumbnail or BotImages.ThumbnailMissing
        )
    
################################################################################
    def main_image_status(self) -> Embed:
        
        return U.make_embed(
            title="__Main Image__",
            description=(
                "This image is displayed in the bottom center of your profile.\n"
                "To change this image, use the buttons below."
            ),
            image_url=self._main_image or BotImages.MainImageMissing
        )
    
################################################################################
    async def thumbnail_management(self, interaction: Interaction) -> None:

        embed = self.thumbnail_status()
        view = ProfileThumbnailStatusView(interaction.user, self)
        
        await interaction.response.send_message(embed=embed, view=view)
        await view.wait()
        
################################################################################
    async def main_image_management(self, interaction: Interaction) -> None:

        embed = self.main_image_status()
        view = ProfileMainImageStatusView(interaction.user, self)
        
        await interaction.response.send_message(embed=embed, view=view)
        await view.wait()
        
################################################################################
    async def set_thumbnail(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Thumbnail Image__",
            description=(
                "Please send the image you would like to set as your thumbnail.\n"
                "*(This image will be displayed in the upper-right corner of your profile.)*"
            )
        )
        
        if image := await U.wait_for_image(interaction, prompt):
            self.thumbnail = image
            
################################################################################
    async def remove_thumbnail(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Remove Thumbnail__",
            description=(
                "Are you sure you want to remove your current thumbnail image?"
            )
        )
        view = ConfirmCancelView(interaction.user)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.thumbnail = None
        
################################################################################
    async def set_main_image(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Main Image__",
            description=(
                "Please send the image you would like to set as your main image.\n"
                "*(This image will be displayed bottom-center on your profile.)*"
            )
        )
        
        if image := await U.wait_for_image(interaction, prompt):
            self.main_image = image
            
################################################################################
    async def remove_main_image(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Remove Main Image__",
            description=(
                "Are you sure you want to remove your current main image?"
            )
        )
        view = ConfirmCancelView(interaction.user)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.main_image = None
        
################################################################################
    async def add_additional_image(self, interaction: Interaction) -> None:
        
        if len(self.additional) >= MAX_ADDITIONAL_IMAGES:
            error = U.make_error(
                title="Image Maximum Reached",
                message=(
                    f"You already have the maximum of `{MAX_ADDITIONAL_IMAGES}` "
                    f"additional images on your profile."
                ),
                solution="Sorry, I can't add any more because of formatting restrictions. :("
            )
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        prompt = U.make_embed(
            title="__Additional Image__",
            description=(
                "Please send the image you would like to add to your profile.\n"
                "*(This image will be displayed in the additional images section of your profile.)*"
            )
        )
        
        if image := await U.wait_for_image(interaction, prompt):
            self.additional.append(AdditionalImage.new(self, image))
            
################################################################################
    async def paginate_additional(self, interaction: Interaction) -> None:
        
        pages = [a.page() for a in self.additional]
        frogginator = AdditionalImageFrogginator(pages, self)
        await frogginator.respond(interaction)
    
################################################################################
    