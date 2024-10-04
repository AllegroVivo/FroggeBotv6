from __future__ import annotations

from discord import Cog, user_command, ApplicationContext, User
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Classes import FroggeBot
################################################################################
class UserCommands(Cog):

    def __init__(self, bot: FroggeBot):

        self.bot: FroggeBot = bot

################################################################################
    @user_command(name="VIP Member Menu")
    async def vip_member_menu(self, ctx: ApplicationContext, user: User) -> None:

        guild = self.bot[ctx.guild.id]
        await guild.vip_manager.vip_member_menu_ctx(ctx.interaction, user)

################################################################################
    @user_command(name="Employee Status")
    async def employee_status(self, ctx: ApplicationContext, user: User) -> None:

        guild = self.bot[ctx.guild.id]
        await guild.staff_manager.user_menu(ctx.interaction, user)
        
################################################################################
def setup(bot: FroggeBot) -> None:

    bot.add_cog(UserCommands(bot))

################################################################################
