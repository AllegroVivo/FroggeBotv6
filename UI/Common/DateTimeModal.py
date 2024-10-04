from __future__ import annotations
from datetime import datetime
from typing import Optional

from discord import Interaction
from Utilities.ErrorMessage import ErrorMessage

from UI.Common.BasicTextModal import BasicTextModal
from UI.Common.InstructionsInfo import InstructionsInfo
################################################################################

__all__ = ("DateTimeModal",)

################################################################################
class DateTimeModal(BasicTextModal):

    def __init__(
        self,
        dt_type: str,
        current_dt: Optional[datetime]
    ):

        super().__init__(
            title=f"{dt_type} Date/Time Entry",
            attribute="Date/Time",
            cur_val=current_dt.strftime("%m/%d/%y %I:%M %p") if current_dt else None,
            example="e.g. '4/20/25 4:20 pm'",
            max_length=20,
            required=False,
            instructions=InstructionsInfo(
                placeholder="Enter the date & time.",
                value=(
                    "Enter the date and time for the object in question. "
                    "The format should be 'MM/DD/YY HH:MM AM/PM'."
                )
            )
        )
        
    async def callback(self, interaction: Interaction):
        raw_dt = self.children[1].value
        if raw_dt:
            try:
                parsed = datetime.strptime(raw_dt, "%m/%d/%y %I:%M %p")
            except ValueError:
                try:
                    parsed = datetime.strptime(raw_dt, "%m/%d/%y %I:%M%p")
                except ValueError:
                    error = InvalidDatetime(raw_dt)
                    self.stop()
                    await interaction.respond(embed=error, ephemeral=True)
                    return
                else:
                    self.value = parsed
            else:
                self.value = parsed
        else:
            self.value = None

        await self.dummy_response(interaction)
        
        self.complete = True
        self.stop()                
        
################################################################################
class InvalidDatetime(ErrorMessage):

    def __init__(self, value: str):
        super().__init__(
            title="Invalid Date/Time Entry",
            description=f"Invalid Value: {value}",
            message="The date/time you entered is invalid.",
            solution="Please enter a valid date/time in the format '`MM/DD/YY HH:MM AM/PM`'.",
        )

################################################################################
        