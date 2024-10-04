from __future__ import annotations

from typing import List

from discord import Interaction, InputTextStyle
from discord.ui import InputText

from UI.Common import FroggeModal
from Utilities import Utilities as U
################################################################################

__all__ = ("ProfileLikesModal",)

################################################################################
class ProfileLikesModal(FroggeModal):

    def __init__(self, cur_val: List[str], likes: bool):
        
        section = "likes" if likes else "dislikes"
        super().__init__(title=f"{section.title()} Entry")

        instructions = (
            f"Enter a list of your {section} separated "
            f"by commas. Minimum three is suggested. Your likes list should "
            "be LONGER than your dislikes to avoid formatting issues."
        )
        cur_val = ", ".join(cur_val) if cur_val else None

        self.add_item(
            InputText(
                style=InputTextStyle.multiline,
                label="Instructions",
                placeholder=f"Enter your {section} section content.",
                value=instructions,
                required=False
            )
        )

        self.add_item(
            InputText(
                style=InputTextStyle.multiline,
                label=section.title(),
                placeholder="eg. 'Moist Climates, Long Walks Around the Pond, Flies'",
                value=cur_val,
                required=False,
                max_length=300
            )
        )

    async def callback(self, interaction: Interaction):
        if self.children[1].value:
            self.value = [U.titleize(i.strip()) for i in self.children[1].value.split(",")]

        self.complete = True

        await interaction.response.edit_message()
        self.stop()

################################################################################
