from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Interaction, User
from discord.ui import Select

from UI.Common import FroggeView, CloseMessageButton
from UI.Profiles import CustomOrientationModal
from Enums import Orientation

if TYPE_CHECKING:
    from Classes import ProfileAtAGlance
################################################################################

__all__ = ("OrientationSelectView",)

################################################################################        
class OrientationSelectView(FroggeView):

    def __init__(self, user: User, aag: ProfileAtAGlance):

        super().__init__(user, aag)

        item_list = [
            OrientationSelect(),
            CloseMessageButton()
        ]
        for item in item_list:
            self.add_item(item)

################################################################################        
class OrientationSelect(Select):

    def __init__(self):
        super().__init__(
            placeholder="Select Your Orientation...",
            options=Orientation.select_options(),
            disabled=False,
            row=0
        )

    async def callback(self, interaction: Interaction):
        response = Orientation(int(self.values[0]))

        if response is Orientation.Custom:
            modal = CustomOrientationModal(self.view.ctx.orientation)

            await interaction.response.send_modal(modal)
            await modal.wait()

            if not modal.complete:
                return

            response = modal.value
        else:
            await interaction.response.edit_message()

        self.view.value = response
        self.view.complete = True

        await self.view.stop()  # type: ignore

################################################################################
