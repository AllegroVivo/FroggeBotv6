from __future__ import annotations

from typing import Optional, Union

from Enums import Gender
from UI.Common import BasicTextModal, InstructionsInfo
################################################################################

__all__ = ("CustomGenderModal",)

################################################################################
class CustomGenderModal(BasicTextModal):

    def __init__(self, cur_val: Optional[Union[Gender, str]]):

        super().__init__(
            title="Set Custom Gender",
            attribute="Gender",
            cur_val=cur_val if isinstance(cur_val, str) else None,
            example="eg. 'Amphibian'",
            max_length=30,
            required=True,
            instructions=InstructionsInfo(
                placeholder="Enter your custom gender identity below.",
                value=(
                    "Enter your custom gender identity in the box below.\n"
                    "You can choose your preferred pronouns after this."
                )
            )
        )

################################################################################
