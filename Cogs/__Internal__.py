from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Cog, Guild, ApplicationContext, DiscordException
from discord.ext.tasks import loop

from logger import log

if TYPE_CHECKING:
    from Classes import FroggeBot
################################################################################
class Internal(Cog):

    def __init__(self, bot: FroggeBot):

        self.bot: FroggeBot = bot

################################################################################
    @Cog.listener("on_ready")
    async def load_internals(self) -> None:

        log.info(None, "Loading internals...")
        await self.bot.load_all()
        
        log.info(None, "Starting tasks...")
        self.check_room_end_times.start()
        
        log.info(None, "FroggeBot Online!")

################################################################################
    @Cog.listener("on_guild_join")
    async def on_guild_join(self, guild: Guild) -> None:

        log.info(None, f"Joined guild: {guild.name} ({guild.id})")

        existing = self.bot.api.check_guild(guild.id)
        if existing["guild_id"] != 0:
            log.info(None, f"Guild {guild.name} already exists in the database.")
            return

        log.info(None, f"Guild {guild.name} does not exist in the database.")

        # If not existing, we add it to the database
        payload = self.bot.api.create_guild(guild.id)
        frogge = self.bot.guild_manager.init_guild(guild)
        await frogge.load_all(payload)

        log.info(None, f"Guild {guild.name} added to the database.")

################################################################################
    @Cog.listener("on_member_join")
    async def on_member_join(self, member) -> None:

        await self.bot[member.guild.id].log.member_join(member)

################################################################################
    @Cog.listener("on_member_remove")
    async def on_member_remove(self, member) -> None:

        await self.bot[member.guild.id].log.member_left(member)

################################################################################
    @Cog.listener("on_application_command_error")
    async def on_application_command_error(self, ctx: ApplicationContext, error: DiscordException) -> None:

        await self.bot.report_error(ctx, error)

################################################################################
    @loop(minutes=1)
    async def check_room_end_times(self) -> None:

        for frogge in self.bot.guild_manager.fguilds:
            await frogge.rooms_manager.check_end_times()

################################################################################
def setup(bot: FroggeBot) -> None:

    bot.add_cog(Internal(bot))

################################################################################
