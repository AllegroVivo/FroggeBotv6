from __future__ import annotations
from discord import Colour, Interaction
from typing import Optional
from Utilities.ErrorMessage import ErrorMessage
from UI.Common.BasicTextModal import BasicTextModal
from UI.Common.InstructionsInfo import InstructionsInfo
################################################################################

__all__ = ("AccentColorModal",)

################################################################################
class AccentColorModal(BasicTextModal):

    def __init__(self, cur_val: Optional[Colour]):

        super().__init__(
            title="Set Accent Color",
            attribute="Accent Color HEX",
            cur_val=str(cur_val).upper() if cur_val is not None else None,
            example="e.g. '#4ABC23'",
            min_length=6,
            max_length=7,
            required=False,
            instructions=InstructionsInfo(
                placeholder="Enter your desired accent color.",
                value=(
                    "Enter the 6-character HEX code for your desired accent color.\n"
                    "Google 'Color Picker' if you have questions."
                )
            )
        )
        
    async def callback(self, interaction: Interaction):
        raw_color = self.children[1].value.upper()

        # Step 1: Remove the leading # if it exists
        if raw_color.startswith("#"):
            raw_color = raw_color[1:]

        # Step 2: Validate the length and characters
        if len(raw_color) != 6 or not all(c in "0123456789ABCDEF" for c in raw_color):
            error = InvalidColor(self.children[1].value)
            await interaction.response.send_message(embed=error, ephemeral=True)
            return

        # Step 3: Convert to Colour if valid
        try:
            color = Colour(int(raw_color, 16)) if raw_color else None
        except ValueError:
            error = InvalidColor(self.children[1].value)
            await interaction.response.send_message(embed=error, ephemeral=True)
        else:
            self.value = color
            self.complete = True

        await self.dummy_response(interaction)
        self.stop()
        
################################################################################
class InvalidColor(ErrorMessage):

    def __init__(self, invalid_value: str):

        super().__init__(
            title="Invalid Color Value",
            description=f"You entered `{invalid_value}` for your accent color.",
            message="The value you entered in the modal couldn't be parsed into a HEX color.",
            solution=(
                "Ensure you're entering a valid HEX code comprised of 6 characters, "
                "numbers `0 - 9` and letters `A - F`."
            )
        )

################################################################################

