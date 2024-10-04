from typing import List

from discord import SelectOption

from ._Enum import FroggeEnum
################################################################################
class Race(FroggeEnum):

    Aura = 1
    Elezen = 2
    FantasiaAddict = 3
    Hrothgar = 4
    Hyur = 5
    Lalafell = 6
    Miqote = 7
    Roegadyn = 8
    Viera = 9
    Custom = 10

################################################################################
    @property
    def proper_name(self) -> str:

        if self.value == 1:
            return "Au ra"
        elif self.value == 3:
            return "Fantasia Addict"
        elif self.value == 7:
            return "Miqo'te"
        else:
            return self.name
        
################################################################################
