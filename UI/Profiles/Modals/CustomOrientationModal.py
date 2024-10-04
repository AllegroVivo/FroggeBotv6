from __future__ import annotations

from typing import Optional, Union

from Enums import Orientation
from UI.Common import BasicTextModal
################################################################################

__all__ = ("CustomOrientationModal",)

################################################################################
class CustomOrientationModal(BasicTextModal):

    def __init__(self, cur_value: Optional[Union[Orientation, str]]):
        
        super().__init__(
            title="Set Custom Sexual Orientation",
            attribute="Sexual Orientation",
            cur_val=cur_value if isinstance(cur_value, str) else None,
            example="eg. 'Frogge'",
            max_length=40,
            required=False,
        )

################################################################################
