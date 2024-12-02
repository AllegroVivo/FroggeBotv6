import random
from typing import TYPE_CHECKING

from discord import (
    ApplicationContext,
    Cog,
    Option,
    SlashCommandOptionType,
    slash_command
)
from requests import delete

if TYPE_CHECKING:
    from Classes import FroggeBot
################################################################################
class General(Cog):
    
    def __init__(self, bot: "FroggeBot"):
        
        self.bot: "FroggeBot" = bot
    
################################################################################
    @slash_command(
        name="verify",
        description="Verify your FFXIV Lodestone Character."
    )
    async def user_verify(self, ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.verification_manager.verify(ctx.interaction)
        
################################################################################
    @slash_command(
        name="addtickets",
        description="Add x tickets to the current active raffle for a given user.",
    )
    async def add_tickets(
        self,
        ctx: ApplicationContext,
        user: Option(
            SlashCommandOptionType.user,
            name="user",
            description="The user to add tickets for.",
            required=True
        ),
        qty: Option(
            SlashCommandOptionType.integer,
            name="quantity",
            description="The number of tickets to add.",
            required=True
        )
    ):
        
        guild = self.bot[ctx.guild_id]
        await guild.activities_manager.raffle_manager.add_tickets(ctx.interaction, user, qty)

################################################################################
    @slash_command(
        name="help",
        description="Get a list of available commands."
    )
    async def help(self, ctx: ApplicationContext) -> None:

        await self.bot.help(ctx.interaction)

################################################################################
def setup(bot: "FroggeBot") -> None:

    bot.add_cog(General(bot))
                
################################################################################
    