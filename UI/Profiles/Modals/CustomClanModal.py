from __future__ import annotations

from typing import Optional, Union

from Enums import Clan
from UI.Common import InstructionsInfo, BasicTextModal
################################################################################

__all__ = ("CustomClanModal",)

################################################################################
class CustomClanModal(BasicTextModal):
    
    def __init__(self, cur_clan: Optional[Union[Clan, str]]):
        
        super().__init__(
            title="Set Custom Clan",
            attribute="Clan",
            cur_val=cur_clan if isinstance(cur_clan, str) else None,
            example="eg. 'Pad Leaper'",
            max_length=25,
            required=False,
            instructions=InstructionsInfo(
                placeholder="Enter your custom Clan value below.",
                value=(
                    "Enter your custom Clan value below. This isn't required, and if \n"
                    "you don't want to enter one, simply submit a blank dialog."
                )
            )
        )

################################################################################
