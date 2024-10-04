from typing import List

from discord import SelectOption

from ._Enum import FroggeEnum
################################################################################
class ProfileItem(FroggeEnum):

    CustomURL = 1
    Color = 2
    Jobs = 3
    Rates = 4
    Gender = 5
    Race = 6
    Orientation = 7
    Height = 8
    Age = 9
    Mare = 10
    World = 11
    Likes = 12
    Dislikes = 13
    Personality = 14
    AboutMe = 15
    Thumbnail = 16
    MainImage = 17

################################################################################
    @property
    def proper_name(self) -> str:
        
        if self.value == 1:
            return "Custom URL"
        elif self.value == 15:
            return "About Me"
        elif self.value == 17:
            return "Main Image"
        
        return self.name
    
################################################################################  
        