from typing import List

from discord import SelectOption

from ._Enum import FroggeEnum
################################################################################
class ReactionRoleMessageType(FroggeEnum):

    Normal = 1  # Hands out roles when you click on them, does what you'd expect
    Unique = 2  # Only lets one role from the message be picked up at once
    Verify = 3  # Roles can only be picked up, not removed
    # Drop = 4  # Roles can only be removed, not picked up
    # Reverse = 5  # Adding a reaction removes the role, removing the reaction adds a role
    # Limit = 6  # Limits the total number of roles one can pick up from this message
    # Binding = 7  # You can only choose one role, and you can not swap between roles
    # Temporary = 8  # Roles are removed after a certain amount of time

################################################################################
    @property
    def description(self) -> str:

        match self:
            case ReactionRoleMessageType.Normal:
                return "Hands out roles when you click on them, does what you'd expect"
            case ReactionRoleMessageType.Unique:
                return "Only lets one role from the message be picked up at once"
            case ReactionRoleMessageType.Verify:
                return "Roles can only be picked up, not removed"
            # case ReactionRoleMessageType.Drop:
            #     return "Roles can only be removed, not picked up"
            # case ReactionRoleMessageType.Reverse:
            #     return "Adding a reaction removes the role, removing the reaction adds a role"
            # case ReactionRoleMessageType.Limit:
            #     return "Limits the total number of roles one can pick up from this message"
            # case ReactionRoleMessageType.Binding:
            #     return "You can only choose one role, and you can not swap between roles"
            # case ReactionRoleMessageType.Temporary:
            #     return "Roles are removed after a certain amount of time"
            case _:
                return "Unknown"

################################################################################
    @property
    def select_option(self) -> SelectOption:

        return SelectOption(
            label=self.proper_name,
            value=str(self.value),
            description=self.description
        )

################################################################################
