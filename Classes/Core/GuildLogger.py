from __future__ import annotations

import os
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, List

from discord import (
    TextChannel,
    Embed,
    Colour,
    Member,
    User,
    EmbedField,
    File,
)

from Enums import LogType
from Utilities import Utilities as U, FroggeColor

if TYPE_CHECKING:
    from Classes import *
################################################################################

__all__ = ("GuildLogger",)

################################################################################
class GuildLogger:

    __slots__ = (
        "_guild",
    )

################################################################################
    def __init__(self, state: GuildData) -> None:

        self._guild: GuildData = state

################################################################################
    async def log_channel(self) -> Optional[TextChannel]:

        return await self._guild.config.log_channel

################################################################################
    async def _log(self, message: Embed, action: LogType, **kwargs) -> None:

        if await self.log_channel() is None:
            return

        try:
            message.colour = LOG_COLORS[action]
        except KeyError:
            print(f"Invalid action passed to LOG_COLORS: '{action}'")
            message.colour = Colour.embed_background()

        channel = await self.log_channel()
        await channel.send(embed=message, **kwargs)
       
################################################################################
    async def _member_event(self, member: Member, _type: LogType) -> None:

        word = "joined" if _type == LogType.MemberJoin else "left"
        embed = U.make_embed(
            title=f"Member {word.title()}!",
            description=f"{member.mention} has `{word}` the server!",
            thumbnail_url=member.display_avatar.url,
            timestamp=True
        )

        await self._log(embed, _type)

################################################################################
    async def member_join(self, member: Member) -> None:

        await self._member_event(member, LogType.MemberJoin)

################################################################################
    async def member_left(self, member: Member) -> None:
    
        await self._member_event(member, LogType.MemberLeave)

################################################################################
    async def member_deleted(self, user: User) -> None:
        
        embed = U.make_embed(
            title="User Deleted",
            description=f"User {user.mention} ({user.name}) has been deleted!",
            timestamp=True
        )
        
        await self._log(embed, LogType.UserDeleted)
        
################################################################################
    async def dms_closed(self, user: User) -> None:
        
        embed = U.make_embed(
            title="DMs Closed",
            description=f"{user.mention} ({user.name}) was unable to be DM'd by the bot!",
            timestamp=True
        )
        
        await self._log(embed, LogType.DMsClosed)
        
################################################################################
    async def bulk_tier_reassignment(self, members: List[VIPMember], new_tier: VIPTier) -> None:

        for member in members:
            perks_summary = ""
            for p in member.tier.perks:
                status = "Not Redeemed"
                for override in member.overrides:
                    if override.perk.id == p.id:
                        status = override.level.proper_name
                perks_summary += f"* `{p.text}` - `{status}`\n"
            if not perks_summary:
                perks_summary = "`No Perks Defined in Previous Tier`"

            user = await member.user.get(self._guild)
            embed = U.make_embed(
                title="Bulk Tier Reassignment",
                description=(
                    f"**{user.mention}** ({user.display_name}) has "
                    f"been moved to the `{new_tier.name}` tier!"
                ),
                fields=[
                    EmbedField(
                        name="__Perks Summary__",
                        value=perks_summary,
                        inline=False
                    )
                ],
                timestamp=True
            )
            await self._log(embed, LogType.BulkVIPTierReassignment)
            
################################################################################
    async def verification_submitted(self, user: User, char_name: str) -> None:

        embed = U.make_embed(
            title="Verification Submitted",
            description=(
                f"User `{user.display_name}` (`{user.id}`) has verified their account!\n\n"

                "__Character Name:__\n"
                f"`{char_name}`"
            ),
            timestamp=True
        )

        await self._log(embed, LogType.VerificationSubmitted)

################################################################################
    async def user_not_found(self, user: User) -> None:

        embed = U.make_embed(
            title="User Not Found",
            description=(
                f"User {user.mention} ({user.display_name}) was not found by "
                f"Discord! This user may have deleted their account."
            ),
            timestamp=True
        )

        await self._log(embed, LogType.UserNotFound)

################################################################################
    async def giveaway_winner_notified(self, winner: GiveawayEntry) -> None:

        user = await winner.user
        embed = U.make_embed(
            title="Giveaway Winner Notified",
            description=(
                f"User {user.mention} ({user.display_name}) has been "
                f"notified of their win in giveaway `{winner._parent.name}`!"
            ),
            timestamp=True
        )

        await self._log(embed, LogType.GiveawayWinnerNotified)

################################################################################
    async def activity_rolled(self, activity: BaseActivity, roller: Optional[User]) -> None:

        winner_list = [await w.user for w in activity.winners]
        winner_str = "\n".join(
            f"{user.mention} - ({user.display_name})" for user in winner_list
        )

        activity_name = activity.activity_name
        embed = U.make_embed(
            title=f"{activity_name} Rolled",
            description=(
                f"{activity_name} `{activity.name}` has been rolled!\n\n"

                f"__Winner(s):__\n"
                f"{winner_str}"
            ),
            timestamp=True
        )

        entry_data = activity.generate_entries_report_str(True)
        entry_data += f"\n\nRolled at {datetime.now().strftime('%m-%d-%y %H:%M:%S')}"
        if roller is not None:
            entry_data += f" by {roller.display_name} ({roller.id})"
        else:
            entry_data += " by the auto-roll system"

        filename = f"{activity.name}-{datetime.now().strftime('%m-%d-%y')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(entry_data)

        await self._log(embed, LogType.ActivityRolled, file=File(filename))

        try:
            os.remove(filename)
        except FileNotFoundError:
            pass

################################################################################
    async def raffle_winner_notified(self, winner: RaffleEntry) -> None:

        user = await winner.user
        embed = U.make_embed(
            title="Raffle Winner Notified",
            description=(
                f"User {user.mention} ({user.display_name}) has been "
                f"notified of their win in raffle `{winner._parent.name}`!"
            ),
            timestamp=True
        )

        await self._log(embed, LogType.RaffleWinnerNotified)

################################################################################
LOG_COLORS: Dict[LogType, FroggeColor] = {
    LogType.MemberJoin: FroggeColor.brand_green(),
    LogType.MemberLeave: FroggeColor.brand_red(),
    LogType.PositionCreated: FroggeColor.cornflower_blue(),
    LogType.PositionUpdated: FroggeColor.light_yellow(),
    LogType.PositionRemoved: FroggeColor.orchid(),
    LogType.ConfigurationUpdated: FroggeColor.lavender(),
    LogType.UserDeleted: FroggeColor.red_violet(),
    LogType.DMsClosed: FroggeColor.medium_violet_red(),
    LogType.BulkVIPTierReassignment: FroggeColor.dark_orange(),
    LogType.VIPExpired: FroggeColor.medium_purple(),
    LogType.GiveawayRolled: FroggeColor.fuchsia(),
    LogType.VerificationSubmitted: FroggeColor.light_green(),
    LogType.ActivityRolled: FroggeColor.blue_green(),
    LogType.UserNotFound: FroggeColor.royal_blue(),
    LogType.GiveawayWinnerNotified: FroggeColor.light_sea_green(),
    LogType.RaffleWinnerNotified: FroggeColor.steel_blue(),
}
################################################################################
