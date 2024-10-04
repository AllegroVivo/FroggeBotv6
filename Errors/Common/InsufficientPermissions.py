from __future__ import annotations

from typing import Optional

from discord.abc import GuildChannel

from Utilities import ErrorMessage
################################################################################
__all__ = ("InsufficientPermissions",)
################################################################################
class InsufficientPermissions(ErrorMessage):

    def __init__(self, channel: Optional[GuildChannel], permissions_needed: str):
    
        super().__init__(
            title="Insufficient Permissions",
            message=(
                f"The bot does not have the required permission(s) `{permissions_needed}` "
                f"to perform that action."
            ) if channel is None else (
                f"You do not have the required permission(s) `{permissions_needed}` "
                f"to perform that action in the channel {channel.mention}."
            ),
            solution="Please contact a server administrator for assistance."
        )

################################################################################
