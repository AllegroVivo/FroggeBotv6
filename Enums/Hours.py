from typing import List

from datetime import time
from discord import SelectOption

from ._Enum import FroggeEnum
################################################################################
class Hours(FroggeEnum):

    TwelveAM = 0
    OneAM = 1
    TwoAM = 2
    ThreeAM = 3
    FourAM = 4
    FiveAM = 5
    SixAM = 6
    SevenAM = 7
    EightAM = 8
    NineAM = 9
    TenAM = 10
    ElevenAM = 11
    TwelvePM = 12
    OnePM = 13
    TwoPM = 14
    ThreePM = 15
    FourPM = 16
    FivePM = 17
    SixPM = 18
    SevenPM = 19
    EightPM = 20
    NinePM = 21
    TenPM = 22
    ElevenPM = 23

################################################################################
    @property
    def proper_name(self) -> str:

        if self.value == 0:
            return "12:xx AM"
        elif self.value == 1:
            return "1:xx AM"
        elif self.value == 2:
            return "2:xx AM"
        elif self.value == 3:
            return "3:xx AM"
        elif self.value == 4:
            return "4:xx AM"
        elif self.value == 5:
            return "5:xx AM"
        elif self.value == 6:
            return "6:xx AM"
        elif self.value == 7:
            return "7:xx AM"
        elif self.value == 8:
            return "8:xx AM"
        elif self.value == 9:
            return "9:xx AM"
        elif self.value == 10:
            return "10:xx AM"
        elif self.value == 11:
            return "11:xx AM"
        elif self.value == 12:
            return "12:xx PM"
        elif self.value == 13:
            return "1:xx PM"
        elif self.value == 14:
            return "2:xx PM"
        elif self.value == 15:
            return "3:xx PM"
        elif self.value == 16:
            return "4:xx PM"
        elif self.value == 17:
            return "5:xx PM"
        elif self.value == 18:
            return "6:xx PM"
        elif self.value == 19:
            return "7:xx PM"
        elif self.value == 20:
            return "8:xx PM"
        elif self.value == 21:
            return "9:xx PM"
        elif self.value == 22:
            return "10:xx PM"
        elif self.value == 23:
            return "11:xx PM"
        else:
            return self.name

################################################################################
    def __gt__(self, other) -> bool:

        return self.value > other.value
    
################################################################################
    def __lt__(self, other) -> bool:

        return self.value < other.value
    
################################################################################
    @staticmethod
    def limited_select_options(start: time, end: time) -> List[SelectOption]:
            
        # Handling the wrap-around scenario
        if end.hour <= start.hour:
            options = [
                o for o in Hours.select_options()
                if start.hour <= int(o.value) < 24 or 0 <= int(o.value) <= end.hour
            ]
        else:
            options = [
                o for o in Hours.select_options()
                if start.hour <= int(o.value) <= end.hour
            ]
            
        return options
        
################################################################################
        