from ._Enum import FroggeEnum
################################################################################
class ChannelDesignation(FroggeEnum):
    
    LogStream = 0
    Scheduling = 1
    Profile = 2
    Applications = 3
    Giveaways = 4
    Raffles = 5
    Tournaments = 6

################################################################################
    @property
    def proper_name(self) -> str:
        
        if self is ChannelDesignation.LogStream:
            return "Log Stream"
        
        return self.name
    
################################################################################
    