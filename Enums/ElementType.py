from typing import List

from discord import SelectOption

from ._Enum import FroggeEnum
################################################################################
__all__ = ("ElementType",)
################################################################################
class ElementType(FroggeEnum):
    
    Address = 0
    Theme = 1
    Syncshell = 2
    PartyFinder = 3
    ShoutRun = 4
    Greeting = 5
    VenueShout = 6
    DJInfo = 7
    
    Miscellaneous = 99

################################################################################
    @property
    def proper_name(self) -> str:
        
        if self.value == 3:
            return "Party Finder"
        elif self.value == 4:
            return "Shout Run"
        elif self.value == 6:
            return "Venue Shout"
        elif self.value == 7:
            return "DJ Info"
        
        return self.name
    
################################################################################
    