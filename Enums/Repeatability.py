from typing import List

from discord import SelectOption

from ._Enum import FroggeEnum
################################################################################
class Repeatability(FroggeEnum):
    
    Monthly = 1
    Renewable = 2
    OneTime = 3

################################################################################
    @property
    def proper_name(self) -> str:
        
        if self.value == 3:
            return "One Time"
        
        return self.name
        
################################################################################
         