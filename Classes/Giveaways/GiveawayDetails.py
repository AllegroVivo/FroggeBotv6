from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Type, Any, Dict, TypeVar, Optional

from discord import PartialEmoji, Interaction

from Classes.Activities import ActivityDetails
from UI.Common import BasicTextModal, AccentColorModal, DateTimeModal
from Utilities import Utilities as U, FroggeColor

if TYPE_CHECKING:
    from Classes import Giveaway
################################################################################

__all__ = ("GiveawayDetails", )

GD = TypeVar("GD", bound="GiveawayDetails")

################################################################################
class GiveawayDetails(ActivityDetails):

    __slots__ = (
        "_description",
        "_thumbnail",
        "_color",
        "_end_time",
        "_emoji",
    )

################################################################################
    def __init__(self, parent: Giveaway, **kwargs) -> None:

        super().__init__(parent, **kwargs)

        self._description: Optional[str] = kwargs.get("description")
        self._thumbnail: Optional[str] = kwargs.get("thumbnail")
        self._color: Optional[FroggeColor] = kwargs.get("color")
        self._end_time: Optional[datetime] = kwargs.get("end_time")
        self._emoji: Optional[PartialEmoji] = kwargs.get("emoji")

################################################################################
    @classmethod
    def load(cls: Type[GD], parent: Giveaway, data: Dict[str, Any]) -> GD:

        return cls(
            parent=parent,
            name=data["name"],
            prize=data["prize"],
            num_winners=data["num_winners"],
            auto_notify=data["auto_notify"],
            description=data["description"],
            thumbnail=data["thumbnail"],
            color=FroggeColor(data["color"]) if data["color"] else None,
            end_time=datetime.fromisoformat(data["end_time"]) if data["end_time"] else None,
            emoji=PartialEmoji.from_str(data["emoji"]) if data["emoji"] else None
        )

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
    def thumbnail(self, value: str) -> None:

        self._thumbnail = value
        self.update()

################################################################################
    @property
    def color(self) -> Optional[FroggeColor]:

        return self._color

    @color.setter
    def color(self, value: FroggeColor) -> None:

        self._color = value
        self.update()

################################################################################
    @property
    def end(self) -> Optional[datetime]:

        return self._end_time

    @end.setter
    def end(self, value: datetime) -> None:

        self._end_time = value
        self.update()

################################################################################
    @property
    def emoji(self) -> Optional[PartialEmoji]:

        return self._emoji

    @emoji.setter
    def emoji(self, value: PartialEmoji) -> None:

        self._emoji = value
        self.update()

################################################################################
    def update(self) -> None:

        self.bot.api.update_giveaway_details(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "name": self.name,
            "prize": self.prize,
            "num_winners": self.num_winners,
            "auto_notify": self.auto_notify,
            "description": self.description,
            "thumbnail": self.thumbnail,
            "color": self.color.value if self.color else None,
            "end_time": self.end.isoformat() if self.end else None,
            "emoji": str(self.emoji) if self.emoji else None
        }

################################################################################
    async def set_description(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Giveaway Description",
            attribute="Description",
            cur_val=self.description,
            max_length=300,
            example="eg. 'This giveaway is for a free mount!'",
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
            title="__Set Giveaway Thumbnail__",
            description=(
                "Please upload the thumbnail image you would like to use for this giveaway.\n"
                "This image will be displayed in the giveaway post."
            )
        )
        image_url = await U.wait_for_image(interaction, prompt)
        if image_url is None:
            return

        self.thumbnail = image_url

################################################################################
    async def set_color(self, interaction: Interaction) -> None:

        modal = AccentColorModal(self.color)

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.color = modal.value

################################################################################
    async def set_end_date(self, interaction: Interaction) -> None:

        modal = DateTimeModal(dt_type="Giveaway", current_dt=self.end)

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.end = self._parent.py_tz.localize(modal.value)

################################################################################
    async def set_emoji(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Giveaway Emoji__",
            description=(
                "Please send the emoji you would like to use for this giveaway.\n"
                "This emoji will be used on the button to enter the giveaway."
            )
        )
        emoji = await U.listen_for(interaction, prompt, U.MentionableType.Emoji)
        if emoji is None:
            return

        self.emoji = emoji

################################################################################

