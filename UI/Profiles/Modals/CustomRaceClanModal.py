from __future__ import annotations

from typing import Optional, Union

from discord import Interaction, InputTextStyle
from discord.ui import InputText

from UI.Common import FroggeModal
from Enums import Race, Clan
################################################################################

__all__ = ("CustomRaceClanModal",)

################################################################################
class CustomRaceClanModal(FroggeModal):
    
    def __init__(self, cur_race: Optional[Union[Race, str]], cur_clan: Optional[Union[Clan, str]]):
        
        super().__init__(title="Set Custom Race & Clan Values")

        self.add_item(
            InputText(
                style=InputTextStyle.multiline,
                label="Instructions",
                placeholder="Enter your custom race and clan values below.",
                value="Enter your custom race and clan values below. Only race is required.",
                required=False
            )
        )

        self.add_item(
            InputText(
                style=InputTextStyle.singleline,
                label="Race",
                placeholder="eg. 'Amphibarian'",
                value=cur_race if not isinstance(cur_race, Race) else None,
                max_length=25,
                required=True
            )
        )

        self.add_item(
            InputText(
                style=InputTextStyle.singleline,
                label="Clan",
                placeholder="eg. 'Pad Leaper'",
                value=cur_clan if not isinstance(cur_clan, Clan) else None,
                max_length=25,
                required=False
            )
        )
        
    async def callback(self, interaction: Interaction):
        self.value = (
            self.children[1].value,
            self.children[2].value if self.children[2].value else None
        )
        self.complete = True

        await interaction.response.edit_message()
        self.stop()

################################################################################
