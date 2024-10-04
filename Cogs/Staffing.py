from typing import TYPE_CHECKING

from discord import (
    ApplicationContext,
    Cog,
    Option,
    SlashCommandOptionType,
    SlashCommandGroup,
    InteractionContextType,
)

if TYPE_CHECKING:
    from Classes import FroggeBot
################################################################################
class Staffing(Cog):
    
    def __init__(self, bot: "FroggeBot"):
        
        self.bot: "FroggeBot" = bot
        
################################################################################
        
    staffing = SlashCommandGroup(
        name="staff",
        description="Commands for venue staff members.",
        contexts=[InteractionContextType.guild]
    )
    
################################################################################
    @staffing.command(
        name="profile",
        description="Manage your staff character profile(s)."
    )
    async def staffing_profile(self,  ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.profile_manager.user_main_menu(ctx.interaction)

################################################################################
################################################################################
def setup(bot: "FroggeBot") -> None:
    
    bot.add_cog(Staffing(bot))
                
################################################################################
    