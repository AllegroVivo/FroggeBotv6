from typing import List

from discord import SelectOption

from ._Enum import FroggeEnum
################################################################################
class UIComponentType(FroggeEnum):

    ShortText = 0
    LongText = 1
    SelectMenu = 2
    MultiSelect = 3

################################################################################
    @property
    def proper_name(self) -> str:

        if self.value == 0:
            return "Short Text"
        elif self.value == 1:
            return "Long Text"
        elif self.value == 2:
            return "Select Menu"
        elif self.value == 3:
            return "Multi-Select Menu"

        return self.name
    
################################################################################
    