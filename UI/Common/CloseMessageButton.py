from __future__ import annotations

from typing import TYPE_CHECKING, Union

from discord import ButtonStyle, Interaction, Member, User
from discord.ext.pages import Paginator
from discord.ui import Button

from .FroggeView import FroggeView

if TYPE_CHECKING:
    pass
################################################################################

__all__ = (
    "CloseMessageButton",
    "CloseMessageView",
)

################################################################################
class CloseMessageButton(Button):

    def __init__(self):
        super().__init__(
            style=ButtonStyle.success,
            label="Close Message",
            disabled=False,
            row=4
        )

    async def callback(self, interaction: Interaction):
        self.view.value = False
        self.view.complete = True
        self.view._close_on_complete = True

        await interaction.response.edit_message()

        if isinstance(self.view, Paginator):
            await self.view.cancel()
        else:
            await self.view.stop()  # type: ignore

################################################################################
class CloseMessageView(FroggeView):

    def __init__(self, owner: Union[Member, User]):
        super().__init__(owner, close_on_complete=True)

        self.add_item(CloseMessageButton())

################################################################################
