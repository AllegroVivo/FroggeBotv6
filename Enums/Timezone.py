from typing import List

from discord import SelectOption

from ._Enum import FroggeEnum
################################################################################
__all__ = ("Timezone",)
################################################################################
class Timezone(FroggeEnum):

    Null = 0
    MIT = 1
    HST = 2
    AST = 3
    PST = 4
    MST = 5
    CST = 6
    EST = 7
    PRT = 8
    AGT = 9
    CAT = 10
    UTC = 11
    ECT = 12
    EET = 13
    EAT = 14
    NET = 15
    PLT = 16
    BST = 17
    VST = 18
    CTT = 19
    JST = 20
    AET = 21
    SST = 22
    NST = 23

################################################################################
    @property
    def proper_name(self) -> str:

        if self.value == 1:
            return "Midway Island Time"
        elif self.value == 2:
            return "Hawaii Standard Time"
        elif self.value == 3:
            return "Alaska Standard Time"
        elif self.value == 4:
            return "Pacific Standard Time"
        elif self.value == 5:
            return "Mountain Standard Time"
        elif self.value == 6:
            return "Central Standard Time"
        elif self.value == 7:
            return "Eastern Standard Time"
        elif self.value == 8:
            return "Puerto Rico and US Virgin Islands Time"
        elif self.value == 9:
            return "Argentina Standard Time"
        elif self.value == 10:
            return "Central African Time"
        elif self.value == 11:
            return "UTC/Greenwich Mean Time"
        elif self.value == 12:
            return "European Central Time"
        elif self.value == 13:
            return "Eastern European Time"
        elif self.value == 14:
            return "Eastern African Time"
        elif self.value == 15:
            return "Near East Time"
        elif self.value == 16:
            return "Pakistan Lahore Time"
        elif self.value == 17:
            return "Bangladesh Standard Time"
        elif self.value == 18:
            return "Vietnam Standard Time"
        elif self.value == 19:
            return "China Taiwan Time"
        elif self.value == 20:
            return "Japan Standard Time"
        elif self.value == 21:
            return "Australia Eastern Time"
        elif self.value == 22:
            return "Solomon Standard Time"
        elif self.value == 23:
            return "New Zealand Standard Time"
        else:
            return self.name

################################################################################
    @property
    def description(self) -> str:

        if self.value == 0:
            return self.name
        
        offset = self.value - 12
        return f"(UTC{'+' if offset >= 0 else ''}{offset}:00)"

################################################################################
    @classmethod
    def select_options(cls) -> List[SelectOption]:

        return [p.select_option for p in cls if p.value != 0]

################################################################################
    @property
    def select_option(self) -> SelectOption:

        return SelectOption(
            label=self.proper_name, description=self.description, value=str(self.value)
        )

################################################################################
