from typing import List

from discord import SelectOption

from .Race import Race
from ._Enum import FroggeEnum
################################################################################
class Clan(FroggeEnum):

    Dunesfolk = 1
    Duskwight = 2
    Helion = 3
    Hellsguard = 4
    Highlander = 5
    KeeperOfTheMoon = 6
    Midlander = 7
    Plainsfolk = 8
    Raen = 9
    Rava = 10
    SeaWolf = 11
    SeekerOfTheSun = 12
    TheLost = 13
    Veena = 14
    Wildwood = 15
    Xaela = 16
    Custom = 998
    NA = 999
    
################################################################################
    @property
    def proper_name(self) -> str:

        if self.value == 6:
            return "Keeper of the Moon"
        elif self.value == 11:
            return "Sea Wolf"
        elif self.value == 12:
            return "Seeker of the Sun"
        elif self.value == 13:
            return "The Lost"

        return self.name

################################################################################
    @staticmethod
    def select_options_by_race(race: Race) -> List[SelectOption]:

        if race is Race.Aura:
            clan_options = [Clan.Raen, Clan.Xaela, Clan.Custom, Clan.NA]
        elif race is Race.Elezen:
            clan_options = [Clan.Duskwight, Clan.Wildwood, Clan.Custom, Clan.NA]
        elif race is Race.Hrothgar:
            clan_options = [Clan.Helion, Clan.TheLost, Clan.Custom, Clan.NA]
        elif race is Race.Hyur:
            clan_options = [Clan.Highlander, Clan.Midlander, Clan.Custom, Clan.NA]
        elif race is Race.Lalafell:
            clan_options = [Clan.Dunesfolk, Clan.Plainsfolk, Clan.Custom, Clan.NA]
        elif race is Race.Miqote:
            clan_options = [Clan.KeeperOfTheMoon, Clan.SeekerOfTheSun, Clan.Custom, Clan.NA]
        elif race is Race.Roegadyn:
            clan_options = [Clan.Hellsguard, Clan.SeaWolf, Clan.Custom, Clan.NA]
        elif race is Race.Viera:
            clan_options = [Clan.Rava, Clan.Veena, Clan.Custom, Clan.NA]
        else:
            clan_options = [Clan.Custom, Clan.NA]

        return [
            SelectOption(
                label=clan.proper_name,
                value=str(clan.value)
            ) for clan in clan_options
        ]

################################################################################
