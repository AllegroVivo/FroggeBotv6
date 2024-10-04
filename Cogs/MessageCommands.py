from __future__ import annotations

from discord import Cog, message_command, ApplicationContext, Message
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Classes import FroggeBot
################################################################################
class MessageCommands(Cog):

    def __init__(self, bot: FroggeBot):

        self.bot: FroggeBot = bot

################################################################################
    @message_command(name="Roll Giveaway")
    async def roll_giveaway(self, ctx: ApplicationContext, msg: Message) -> None:

        guild = self.bot[ctx.guild.id]
        await guild.activities_manager.giveaway_manager.roll_giveaway_ctx(ctx.interaction, msg)
    
################################################################################
def setup(bot: FroggeBot) -> None:

    bot.add_cog(MessageCommands(bot))

################################################################################
