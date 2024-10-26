from __future__ import annotations

from datetime import datetime, UTC
from typing import TYPE_CHECKING, Optional, List, Any, Type, TypeVar, Dict

from discord import User, Embed, EmbedField, PartialEmoji, SelectOption, Interaction, ChannelType

from Assets import BotEmojis, BotImages
from Classes.Common import ManagedObject
from Errors import InvalidURL
from .FroggeEmbedHeader import FroggeEmbedHeader
from .FroggeEmbedFooter import FroggeEmbedFooter
from .FroggeEmbedImages import FroggeEmbedImages
from .FroggeEmbedField import FroggeEmbedField
from Utilities import Utilities as U, FroggeColor
from UI.Embeds import EmbedStatusView
from UI.Common import BasicTextModal, AccentColorModal, DateTimeModal

if TYPE_CHECKING:
    from Classes import EmbedManager
    from UI.Common import FroggeView
################################################################################

__all__ = ("FroggeEmbed",)

FE = TypeVar("FE", bound="FroggeEmbed")

################################################################################
class FroggeEmbed(ManagedObject):

    __slots__ = (
        "_color",
        "_description",
        "_fields",
        "_footer",
        "_images",
        "_header",
        "_timestamp",
        "_title",
        "_url",
    )

################################################################################
    def __init__(self, mgr: EmbedManager, _id: int, **kwargs) -> None:

        super().__init__(mgr, _id)

        self._color: Optional[FroggeColor] = kwargs.get("color")
        self._description: Optional[str] = kwargs.get("description")
        self._timestamp: Optional[datetime] = kwargs.get("timestamp")
        self._title: Optional[str] = kwargs.get("title")
        self._url: Optional[str] = kwargs.get("url")

        self._header: FroggeEmbedHeader = kwargs.get("header") or FroggeEmbedHeader(self)
        self._footer: FroggeEmbedFooter = kwargs.get("footer") or FroggeEmbedFooter(self)
        self._images: FroggeEmbedImages = kwargs.get("images") or FroggeEmbedImages(self)
        self._fields: List[FroggeEmbedField] = kwargs.get("fields", [])

################################################################################
    @classmethod
    def new(cls: Type[FE], mgr: EmbedManager) -> FE:

        new_data = mgr.bot.api.create_embed(mgr.guild_id)
        return cls(mgr, new_data["id"])

################################################################################
    @classmethod
    def demo(cls: Type[FE], mgr: EmbedManager) -> FE:

        new_data = mgr.bot.api.create_embed(mgr.guild_id)
        new_embed = cls(mgr, new_data["id"])

        new_embed.title = "Demo Embed"
        new_embed.description = (
            "This is a demo embed to help you get started with the embeds module."
        )
        new_embed.color = FroggeColor(int("0x4ABC23", 16))
        new_embed.url = "https://x.com/HomeHopping"
        new_embed.update()

        new_embed.header.text = "Demo Header"
        new_embed.header.icon_url = BotImages.ThumbsUpFrog
        new_embed.header.url = "https://x.com/HomeHopping"
        new_embed.header.update()

        new_embed.footer.text = "Demo Footer"
        new_embed.footer.icon_url = BotImages.ThumbsUpFrog
        new_embed.footer.update()

        new_embed.images.thumbnail = BotImages.ThumbsUpFrog
        new_embed.images.main_image = BotImages.ThumbsUpFrog
        new_embed.images.update()

        return new_embed

################################################################################
    @classmethod
    def load(cls: Type[FE], mgr: EmbedManager, data: Dict[str, Any]) -> FE:

        self: FE = cls.__new__(cls)

        self._id = data["id"]
        self._mgr = mgr

        self._color = FroggeColor(data["color"]) if data["color"] else None
        self._description = data["description"]
        self._timestamp = datetime.fromisoformat(data["timestamp"]) if data["timestamp"] else None
        self._title = data["title"]
        self._url = data["url"]

        self._header = FroggeEmbedHeader.load(self, data["header"])
        self._footer = FroggeEmbedFooter.load(self, data["footer"])
        self._images = FroggeEmbedImages.load(self, data["images"])

        self._fields = [FroggeEmbedField.load(self, field) for field in data["fields"]]

        return self

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
    def description(self) -> Optional[str]:

        return self._description

    @description.setter
    def description(self, value: Optional[str]) -> None:

        self._description = value
        self.update()

################################################################################
    @property
    def timestamp(self) -> Optional[datetime]:

        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: Optional[datetime]) -> None:

        self._timestamp = value
        self.update()

################################################################################
    @property
    def title(self) -> Optional[str]:

        return self._title

    @title.setter
    def title(self, value: Optional[str]) -> None:

        self._title = value
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
    @property
    def header(self) -> FroggeEmbedHeader:

        return self._header

################################################################################
    @property
    def footer(self) -> FroggeEmbedFooter:

        return self._footer

################################################################################
    @property
    def images(self) -> FroggeEmbedImages:

        return self._images

    @property
    def thumbnail(self) -> Optional[str]:

        return self.images.thumbnail

    @property
    def main_image(self) -> Optional[str]:

        return self.images.main_image

################################################################################
    @property
    def fields(self) -> List[FroggeEmbedField]:

        self._fields.sort(key=lambda f: f.order)
        return self._fields

################################################################################
    def update(self) -> None:

        self.bot.api.update_embed(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "color": self.color.value if self.color else None,
            "description": self.description,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "title": self.title,
            "url": self.url,
        }

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_embed(self.id)
        self._mgr._managed.remove(self)

################################################################################
    async def overview(self) -> Embed:

        def emoji(attr: Any) -> str:
            return str(BotEmojis.CheckGreen if attr else BotEmojis.Cross)

        return U.make_embed(
            color=self.color or FroggeColor.embed_background(),
            title=f"__Embed Status Overview__",
            description=(
                f"**Title:**\n"
                f"```{self.title or 'Not Set'}```\n"
                f"**Title URL:** `{self.url or 'Not Set'}`\n"
                f"**Description:**\n"
                f"```{self.description or 'Not Set'}```\n"
            ),
            fields=[
                EmbedField(
                    name="__Color__",
                    value=(
                        f"{BotEmojis.ArrowLeft} -- (__{str(self.color).upper()}__)"
                        if self._color is not None
                        else "`Not Set`"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__Images__",
                    value=(
                        f"**Thumbnail Set:** {emoji(self.thumbnail)}\n"
                        f"**Main Image Set:** {emoji(self.main_image)}\n"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__Header__",
                    value=(
                        f"**Text:** {self.header.text or '`Not Set`'}\n"
                        f"**Icon URL:** {self.header.icon_url or '`Not Set`'}\n"
                        f"**URL:** `{self.header.url or 'Not Set'}`\n"
                    ),
                    inline=False
                ),
                EmbedField(
                    name="__Footer__",
                    value=(
                        f"**Text:** {self.footer.text or '`Not Set`'}\n"
                        f"**Icon URL:** `{self.footer.icon_url or 'Not Set'}`\n"
                    ),
                    inline=False
                ),
            ],
            timestamp=self.timestamp,
        )

################################################################################
    async def status(self) -> Embed:

        return self.compile()

################################################################################
    def compile(self) -> Embed:

        ret = U.make_embed(
            color=self.color,
            title=self.title,
            url=self.url,
            description=self.description,
            timestamp=self.timestamp,
            author_icon=self.header.icon_url,
            author_text=self.header.text,
            author_url=self.header.url,
            footer_icon=self.footer.icon_url,
            footer_text=self.footer.text,
            thumbnail_url=self.images.thumbnail,
            image_url=self.images.main_image,
            fields=[field.compile() for field in self.fields],
            _color_override=True
        )

        # An empty embed resolves to False.
        if not bool(ret):
            ret.title = "No Content"
            ret.description = "This embed has no content."
            ret.colour = FroggeColor.embed_background()

        return ret

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return EmbedStatusView(user, self)

################################################################################
    def select_option(self) -> SelectOption:

        return SelectOption(
            label=self.title or "Untitled Embed",
            value=str(self.id),
        )

################################################################################
    async def set_title(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Embed Title",
            attribute="Title",
            cur_val=self.title,
            max_length=95,
            required=False
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.title = modal.value

################################################################################
    async def set_url(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Embed Title URL",
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
    async def set_description(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Embed Description",
            attribute="Description",
            cur_val=self.description,
            max_length=2000,
            required=False,
            multiline=True
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.description = modal.value

################################################################################
    async def set_color(self, interaction: Interaction) -> None:

        modal = AccentColorModal(self.color)

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.color = modal.value

################################################################################
    async def set_timestamp(self, interaction: Interaction) -> None:

        if self.timestamp is not None:
            try:
                localized = self.py_tz.localize(self.timestamp)
            except:
                localized = self.timestamp
        else:
            localized = self.py_tz.localize(datetime.now())

        modal = DateTimeModal("Embed Timestamp", localized)

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.timestamp = self.py_tz.localize(modal.value) if modal.value else None

################################################################################
    async def header_menu(self, interaction: Interaction) -> None:

        await self.header.menu(interaction)

################################################################################
    async def footer_menu(self, interaction: Interaction) -> None:

        await self.footer.menu(interaction)

################################################################################
    async def images_menu(self, interaction: Interaction) -> None:

        await self.images.menu(interaction)

################################################################################
    async def post(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Post Embed__",
            description=(
                "Please enter the channel you want to post this embed to."
            )
        )
        channel = await U.select_channel(interaction, self.guild, "Embed Channel", prompt)
        if channel is None:
            return

        msg = await channel.send(embed=self.compile())

        confirm = U.make_embed(
            title="__Embed Posted__",
            description=(
                "Your embed has been successfully posted.\n\n"
                
                f"**[Jump to Message]({msg.jump_url})**"
            )
        )
        await interaction.respond(embed=confirm)

################################################################################
