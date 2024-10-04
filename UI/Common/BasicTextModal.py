from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import Interaction, InputTextStyle
from discord.ui import InputText

from .FroggeModal import FroggeModal

if TYPE_CHECKING:
    from .InstructionsInfo import InstructionsInfo
################################################################################

__all__ = ("BasicTextModal",)

################################################################################
class BasicTextModal(FroggeModal):

    def __init__(
        self,
        title: str,
        attribute: str, 
        cur_val: Optional[str] = None,
        example: Optional[str] = None,
        min_length: int = 1,
        max_length: int = 100,
        required: bool = True,
        instructions: Optional[InstructionsInfo] = None,
        multiline: bool = False,
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
                style=(
                    InputTextStyle.multiline if multiline
                    else InputTextStyle.singleline
                ),
                label=attribute,
                placeholder=example,
                value=cur_val,
                min_length=min_length if required else 0,
                max_length=max_length,
                required=required
            )
        )
        
    async def callback(self, interaction: Interaction):
        self.value = (
            (self.children[1].value or None)
            if len(self.children) == 2
            else (self.children[0].value or None)
        )
        self.complete = True
        
        await self.dummy_response(interaction)
        self.stop()
        
################################################################################
