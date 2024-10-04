from typing import List

from discord import SelectOption

from ._Enum import FroggeEnum
################################################################################
class Gender(FroggeEnum):

    Male = 1
    Female = 2
    NonBinary = 3
    Custom = 4

################################################################################
    @property
    def proper_name(self) -> str:

        if self.value == 3:
            return "Non-Binary"

        return self.name
    
################################################################################
    