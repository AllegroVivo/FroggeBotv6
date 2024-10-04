from __future__ import annotations

from typing import Optional, List

from discord import Interaction, InputTextStyle
from discord.ui import InputText

from UI.Common import FroggeModal
################################################################################

__all__ = ("ProfileJobsModal",)

################################################################################
class ProfileJobsModal(FroggeModal):
    
    def __init__(self, cur_val: Optional[List[str]]):
        
        super().__init__(title="Edit Other Jobs")
        
        self.add_item(
            InputText(
                style=InputTextStyle.multiline,
                label="Instructions",
                placeholder="Enter up to three RP professions for your character.",
                value=(
                    "Enter the RP professions to display on your profile. "
                    "(Limit 3 for formatting reasons.)\n"
                    "If you want to delete a job, just empty the corresponding box "
                    "and submit the dialog."
                ),
                required=False
            )
        )

        self.add_item(
            InputText(
                style=InputTextStyle.singleline,
                label="Job #1",
                placeholder="eg. 'Professional Frog'",
                value=cur_val[0] if cur_val is not None and len(cur_val) > 0 else None,
                max_length=20,
                required=False
            )
        )

        self.add_item(
            InputText(
                style=InputTextStyle.singleline,
                label="Job #2",
                placeholder="eg. 'Taco Wrangler'",
                value=cur_val[1] if cur_val is not None and len(cur_val) > 1 else None,
                max_length=20,
                required=False
            )
        )

        self.add_item(
            InputText(
                style=InputTextStyle.singleline,
                label="Job #3",
                placeholder="eg. 'Stunt Camel'",
                value=cur_val[2] if cur_val is not None and len(cur_val) > 2 else None,
                max_length=20,
                required=False
            )
        )
        
    async def callback(self, interaction: Interaction):
        self.value = [
            self.children[1].value if self.children[1].value else None,
            self.children[2].value if self.children[2].value else None,
            self.children[3].value if self.children[3].value else None,
        ]
        self.value = [v for v in self.value if v is not None]
        self.complete = True

        await interaction.response.edit_message()
        self.stop()

################################################################################
