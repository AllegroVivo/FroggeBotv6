from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import Interaction, InputTextStyle
from discord.ui import InputText

from .FroggeModal import FroggeModal
from Utilities.ErrorMessage import ErrorMessage
from Utilities import Utilities as U

if TYPE_CHECKING:
    from .InstructionsInfo import InstructionsInfo
################################################################################

__all__ = ("BasicNumberModal",)

################################################################################
class BasicNumberModal(FroggeModal):

    def __init__(
        self,
        title: str,
        attribute: str, 
        cur_val: Optional[int] = None,
        example: Optional[str] = None,
        max_length: int = 3,
        required: bool = True,
        instructions: Optional[InstructionsInfo] = None,
    ):

        super().__init__(title=title)

        if instructions is not None:
            self.add_item(
                InputText(
                    style=InputTextStyle.multiline,
                    label="Instructions",
                    placeholder=instructions.placeholder,
                    value=instructions.value,
                    required=False
                )
            )
        
        self.add_item(
            InputText(
                style=InputTextStyle.singleline,
                label=attribute,
                placeholder=example,
                value=str(cur_val) if cur_val is not None else None,
                max_length=max_length,
                required=required
            )
        )
        
    async def callback(self, interaction: Interaction):
        raw_value = (
            (self.children[1].value or None)
            if len(self.children) == 2
            else (self.children[0].value or None)
        )
        
        try:
            parsed = U.parse_salary(raw_value)
        except ValueError:
            error = InvalidNumber(raw_value)
            await interaction.respond(embed=error, ephemeral=True)
            return
        else:
            self.value = parsed
        
        self.complete = True
        
        await self.dummy_response(interaction)
        self.stop()
        
################################################################################
class InvalidNumber(ErrorMessage):

    def __init__(self, value: str):
        super().__init__(
            title="Invalid Number",
            description=f"Invalid Value: {value}",
            message="The numerical value you entered is invalid.",
            solution="Enter a whole number.",
        )

################################################################################
        