from typing import List

from discord import SelectOption

from ._Enum import FroggeEnum
################################################################################
class RedemptionLevel(FroggeEnum):

    FullyRedeemed = 0
    PartiallyRedeemed = 1
    NotRedeemed = 2

################################################################################
    @property
    def proper_name(self) -> str:
        
        if self.value == 0:
            return "Fully Redeemed"
        elif self.value == 1:
            return "Partially Redeemed"
        elif self.value == 2:
            return "Not Redeemed"
        
        return self.name
    
################################################################################

    