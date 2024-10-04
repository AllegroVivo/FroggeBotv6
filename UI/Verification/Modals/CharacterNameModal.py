from __future__ import annotations
from discord.ui import InputText
from discord import InputTextStyle, Interaction
from UI.Common import FroggeModal
################################################################################

__all__ = ("CharacterNameModal",)

################################################################################
class CharacterNameModal(FroggeModal):

    def __init__(self):

        super().__init__(title="Lodestone Character Name Entry")

        self.add_item(
            InputText(
                style=InputTextStyle.multiline,
                label="Instructions",
                placeholder="Enter your lodestone character name",
                value=(
                    "Enter your character's name as it appears on the Lodestone. "
                    "This is the name that will be used to verify your character.\n"
                ),
                required=False,
            )
        )
        
        self.add_item(
            InputText(
                style=InputTextStyle.singleline,
                label="Forename",
                placeholder="eg. 'Allegro'",
                max_length=15,
                required=True,
            )
        )

        self.add_item(
            InputText(
                style=InputTextStyle.singleline,
                label="Surname",
                placeholder="eg. 'Vivo'",
                max_length=15,
                required=True,
            )
        )
        
    async def callback(self, interaction: Interaction):
        self.value = (
            self.children[1].value,
            self.children[2].value
        )
        self.complete = True
        
        await self.dummy_response(interaction)
        self.stop()
        
################################################################################
