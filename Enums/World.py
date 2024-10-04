from __future__ import annotations

from typing import List
from typing import TYPE_CHECKING

from discord import SelectOption

from ._Enum import FroggeEnum

if TYPE_CHECKING:
    pass
################################################################################
class World(FroggeEnum):

    Adamantoise = 1
    Alpha = 2
    Balmung = 3
    Behemoth = 4
    Bismarck = 5
    Brynhildr = 6
    Cactuar = 7
    Cerberus = 8
    Coeurl = 9
    Diabolos = 10
    Excalibur = 11
    Exodus = 12
    Faerie = 13
    Famfrit = 14
    Gilgamesh = 15
    Goblin = 16
    Halicarnassus = 17
    Hyperion = 18
    Jenova = 19
    Lamia = 20
    Leviathan = 21
    Lich = 22
    Louisoix = 23
    Maduin = 24
    Malboro = 25
    Marilith = 26
    Mateus = 27
    Midgardsormr = 28
    Moogle = 29
    Odin = 30
    Omega = 31
    Phantom = 32
    Phoenix = 33
    Ragnarok = 34
    Raiden = 35
    Ravana = 36
    Sagittarius = 37
    Sargatanas = 38
    Sephirot = 39
    Seraph = 40
    Shiva = 41
    Siren = 42
    Sophia = 43
    Spriggan = 44
    Twintania = 45
    Ultros = 46
    Zalera = 47
    Zodiark = 48
    Zurvan = 49
    Aegis = 50
    Atomos = 51
    Carbuncle = 52
    Garuda = 53
    Gungnir = 54
    Kujata = 55
    Tonberry = 56
    Typhon = 57
    Alexander = 58
    Bahamut = 59
    Durandal = 60
    Fenrir = 61
    Ifrit = 62
    Ridill = 63
    Tiamat = 64
    Ultima = 65
    Anima = 66
    Asura = 67
    Chocobo = 68
    Hades = 69
    Ixion = 70
    Masamune = 71
    Pandaemonium = 72
    Titan = 73
    Belias = 74
    Mandragora = 75
    Ramuh = 76
    Shinryu = 77
    Unicorn = 78
    Valefor = 79
    Yojimbo = 80
    Zeromus = 81

################################################################################
    @staticmethod
    def select_options_by_dc(dc: FroggeEnum) -> List[SelectOption]:
        
        if dc.value == 1:  # Aether
            world_list = [
                World.Adamantoise,
                World.Cactuar,
                World.Faerie,
                World.Gilgamesh,
                World.Jenova,
                World.Midgardsormr,
                World.Sargatanas,
                World.Siren,
            ]
        elif dc.value == 2:  # Crystal
            world_list = [
                World.Balmung,
                World.Brynhildr,
                World.Coeurl,
                World.Diabolos,
                World.Goblin,
                World.Malboro,
                World.Mateus,
                World.Zalera,
            ]
        elif dc.value == 3:  # Dynamis
            world_list = [
                World.Halicarnassus,
                World.Maduin,
                World.Marilith,
                World.Seraph,
            ]
        elif dc.value == 4:  # Primal
            world_list = [
                World.Behemoth,
                World.Excalibur,
                World.Exodus,
                World.Famfrit,
                World.Hyperion,
                World.Lamia,
                World.Leviathan,
                World.Ultros,
            ]
        elif dc.value == 5:  # Light
            world_list = [
                World.Alpha,
                World.Lich,
                World.Odin,
                World.Phoenix,
                World.Raiden,
                World.Shiva,
                World.Twintania,
                World.Zodiark,
            ]
        elif dc.value == 6:  # Chaos
            world_list = [
                World.Cerberus,
                World.Louisoix,
                World.Moogle,
                World.Omega,
                World.Phantom,
                World.Ragnarok,
                World.Sagittarius,
                World.Spriggan,
            ]
        elif dc.value == 7:  # Materia
            world_list = [
                World.Bismarck,
                World.Ravana,
                World.Sephirot,
                World.Sophia,
                World.Zurvan,
            ]
        elif dc.value == 8:  # Elemental
            world_list = [
                World.Aegis,
                World.Atomos,
                World.Carbuncle,
                World.Garuda,
                World.Gungnir,
                World.Kujata,
                World.Tonberry,
                World.Typhon,
            ]
        elif dc.value == 9:  # Gaia
            world_list = [
                World.Alexander,
                World.Bahamut,
                World.Durandal,
                World.Fenrir,
                World.Ifrit,
                World.Ridill,
                World.Tiamat,
                World.Ultima,
            ]
        elif dc.value == 10:  # Mana
            world_list = [
                World.Anima,
                World.Asura,
                World.Chocobo,
                World.Hades,
                World.Ixion,
                World.Masamune,
                World.Pandaemonium,
                World.Titan,
            ]
        else:  # Meteor
            world_list = [
                World.Belias,
                World.Mandragora,
                World.Ramuh,
                World.Shinryu,
                World.Unicorn,
                World.Valefor,
                World.Yojimbo,
                World.Zeromus,
            ]
            
        return [world.select_option for world in world_list]
    
################################################################################
