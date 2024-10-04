from ._Enum import FroggeEnum
################################################################################
__all__ = ("LogType",)
################################################################################
class LogType(FroggeEnum):
    
    MemberJoin = 0
    MemberLeave = 1
    PositionCreated = 2
    PositionUpdated = 3
    PositionRemoved = 4
    ChannelUpdated = 5
    RoleUpdated = 6
    StaffableEventCreated = 7
    StaffHired = 8
    StaffFired = 9
    CharacterCreated = 10
    TimeClockAction = 11
    VIPTierCreated = 12
    VIPTierRemoved = 13
    VIPPerkAdded = 14
    VIPPerkRemoved = 15
    VIPMemberAdded = 16
    VIPTimeAdded = 17
    ConfigurationUpdated = 18
    UserDeleted = 19
    DMsClosed = 20
    BulkVIPTierReassignment = 21
    VIPExpired = 22
    GiveawayRolled = 23
    VerificationSubmitted = 24
    ActivityRolled = 25
    UserNotFound = 26
    GiveawayWinnerNotified = 27
    RaffleWinnerNotified = 28

################################################################################
