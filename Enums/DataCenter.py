from typing import List, Optional

from discord import SelectOption

from .GameWorld import GameWorld
from ._Enum import FroggeEnum
################################################################################
class DataCenter(FroggeEnum):
    
    Aether = 1
    Crystal = 2
    Dynamis = 3
    Primal = 4
    Light = 5
    Chaos = 6
    Materia = 7
    Elemental = 8
    Gaia = 9
    Mana = 10
    Meteor = 11

################################################################################
    @classmethod
    def from_xiv(cls, xiv_name: Optional[str]) -> Optional["DataCenter"]:
        
        if xiv_name is None:
            return 
        
        for dc in cls:
            if dc.proper_name == xiv_name:
                return dc
            
        raise ValueError(f"Invalid XIV data center name: {xiv_name}")
    
################################################################################
    @classmethod
    def from_world(cls, world: GameWorld) -> "DataCenter":
        
        if world in (
            GameWorld.Adamantoise, GameWorld.Cactuar, GameWorld.Faerie,
            GameWorld.Gilgamesh, GameWorld.Jenova, GameWorld.Midgardsormr,
            GameWorld.Sargatanas, GameWorld.Siren
        ):
            return cls.Aether

        if world in (
            GameWorld.Balmung, GameWorld.Brynhildr, GameWorld.Coeurl,
            GameWorld.Diabolos, GameWorld.Goblin, GameWorld.Malboro,
            GameWorld.Mateus, GameWorld.Zalera
        ):
            return cls.Crystal

        if world in (
            GameWorld.Halicarnassus, GameWorld.Maduin, GameWorld.Marilith,
            GameWorld.Seraph, GameWorld.Cuchulainn, GameWorld.Golem,
            GameWorld.Kraken, GameWorld.Rafflesia,
        ):
            return cls.Dynamis

        if world in (
            GameWorld.Behemoth, GameWorld.Excalibur, GameWorld.Exodus,
            GameWorld.Famfrit, GameWorld.Hyperion, GameWorld.Lamia,
            GameWorld.Leviathan, GameWorld.Ultros
        ):
            return cls.Primal

        if world in (
            GameWorld.Alpha, GameWorld.Lich, GameWorld.Odin, GameWorld.Phoenix,
            GameWorld.Raiden, GameWorld.Shiva, GameWorld.Twintania, GameWorld.Zodiark
        ):
            return cls.Light

        if world in (
            GameWorld.Cerberus, GameWorld.Louisoix, GameWorld.Moogle, GameWorld.Omega,
            GameWorld.Phantom, GameWorld.Ragnarok, GameWorld.Sagittarius, GameWorld.Spriggan
        ):
            return cls.Chaos
        
        raise ValueError(f"Invalid world: {world}")
    
################################################################################
