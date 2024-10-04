from typing import List
from datetime import time
from discord import SelectOption

from ._Enum import FroggeEnum
################################################################################
class Minutes(FroggeEnum):

    Zero = 0
    Fifteen = 15
    Thirty = 30
    FortyFive = 45

################################################################################
    @property
    def proper_name(self) -> str:

        if self.value == 0:
            return "xx:00"
        
        return f"xx:{self.value}"

################################################################################
    def __gt__(self, other) -> bool:

        return self.value > other.value

################################################################################
    def __lt__(self, other) -> bool:

        return self.value < other.value

################################################################################
    @staticmethod
    def limited_select_options(start: time, end: time) -> List[SelectOption]:

        # Handle minute wrap-around if end minutes are less than start minutes
        if end.minute <= start.minute:
            options = [
                o.select_option for o in Minutes
                if start.minute <= o.value < 60 or 0 <= o.value <= end.minute
            ]
        else:
            options = [
                o.select_option for o in Minutes
                if start.minute <= o.value <= end.minute
            ]

        return options

################################################################################
    