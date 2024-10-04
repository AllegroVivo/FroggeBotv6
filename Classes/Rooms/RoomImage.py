from __future__ import annotations

from typing import TYPE_CHECKING, Type, TypeVar

from discord import SelectOption, Interaction

from Classes.Common import Identifiable
from UI.Common import ConfirmCancelView
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import Room, FroggeBot
################################################################################

__all__ = ("RoomImage",)

RI = TypeVar("RI", bound="RoomImage")

################################################################################
class RoomImage(Identifiable):

    __slots__ = (
        "_parent",
        "_url",
    )

################################################################################
    def __init__(self, parent: Room, _id: int, url: str) -> None:

        super().__init__(_id)

        self._parent: Room = parent
        self._url: str = url

################################################################################
    @classmethod
    def new(cls: Type[RI], parent: Room, url: str) -> RI:

        new_data = parent.bot.api.create_room_image(parent.id, url)
        return cls(parent, new_data["id"], url)

################################################################################
    @classmethod
    def load(cls: Type[RI], parent: Room, data: dict) -> RI:

        return cls(
            parent=parent,
            _id=data["id"],
            url=data["url"]
        )

################################################################################
    @property
    def bot(self) -> FroggeBot:

        return self._parent.bot

################################################################################
    @property
    def url(self) -> str:

        return self._url

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_room_image(self.id)
        self._parent._images.remove(self)

################################################################################
    def select_option(self) -> SelectOption:

        return SelectOption(
            label=f"Image {self._parent.images.index(self) + 1}",
            value=str(self.id)
        )

################################################################################
    async def remove(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Image__",
            description=(
                "Are you sure you want to remove this image?"
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.delete()

################################################################################
