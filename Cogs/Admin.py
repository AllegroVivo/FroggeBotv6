from typing import TYPE_CHECKING

from discord import (
    ApplicationContext,
    Cog,
    SlashCommandGroup,
    InteractionContextType,
    NotFound,
    SlashCommandOptionType,
    Option,
    OptionChoice,
)
from Enums import TransactionCategory

if TYPE_CHECKING:
    from Classes import FroggeBot
################################################################################
class Admin(Cog):
    
    def __init__(self, bot: "FroggeBot"):
        
        self.bot: "FroggeBot" = bot
        
################################################################################
        
    admin = SlashCommandGroup(
        name="admin",
        description="Commands for app administration.",
        contexts=[InteractionContextType.guild]
    )
    
################################################################################
    @admin.command(
        name="configuration",
        description="Configure various elements of the bot for this guild."
    )
    async def manage_configuration(self, ctx: ApplicationContext) -> None:
        
        guild = self.bot[ctx.guild_id]
        await guild.config.main_menu(ctx.interaction)
        
################################################################################
    @admin.command(
        name="vip_program",
        description="Manage VIP Program options for this server."
    )
    async def manage_vips(self, ctx: ApplicationContext) -> None:
    
        guild = self.bot[ctx.guild_id]
        await guild.vip_manager.main_menu(ctx.interaction)

################################################################################
    @admin.command(
        name="staffing",
        description="Manage staff members and the application for this server."
    )
    async def manage_staff(self, ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.staff_manager.main_menu(ctx.interaction)

################################################################################
    @admin.command(
        name="forms",
        description="Manage forms for the bot."
    )
    async def forms_menu(self, ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.forms_manager.main_menu(ctx.interaction)

################################################################################
    @admin.command(
        name="profiles",
        description="Manage profiles for the bot."
    )
    async def profiles_menu(self, ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.profile_manager.main_menu(ctx.interaction)

################################################################################
    @admin.command(
        name="events",
        description="Manage events for this server."
    )
    async def manage_events(self, ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.event_manager.main_menu(ctx.interaction)

################################################################################
    @admin.command(
        name="activities",
        description="Manage and review giveaways, raffles, contests, and tournaments for this server."
    )
    async def manage_giveaways(self, ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.activities_manager.main_menu(ctx.interaction)

################################################################################
    @admin.command(
        name="roles",
        description="Manage role reaction messages for this server."
    )
    async def manage_roles(self, ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.roles_manager.main_menu(ctx.interaction)

################################################################################
    @admin.command(
        name="rooms",
        description="Manage rooms and room check settings for this server."
    )
    async def manage_rooms(self, ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.rooms_manager.main_menu(ctx.interaction)

################################################################################
    @admin.command(
        name="embeds",
        description="Manage stored embeds for this server."
    )
    async def manage_verification(self, ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.embed_manager.main_menu(ctx.interaction)

################################################################################
    # @admin.command(
    #     name="finance",
    #     description="Manage transactions and financial settings for this server."
    # )
    # async def manage_finances(self, ctx: ApplicationContext) -> None:
    #
    #     guild = self.bot[ctx.guild_id]
    #     await guild.finance_manager.main_menu(ctx.interaction)

################################################################################
    @admin.command(
        name="hire",
        description="Hire a staff member for your venue."
    )
    async def hire_staff(
        self,
        ctx: ApplicationContext,
        user: Option(
            SlashCommandOptionType.user,
            name="user",
            description="The user to hire.",
            required=True
        )
    ) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.staff_manager.hire(ctx.interaction, user)

################################################################################
    @admin.command(
        name="transaction",
        description="Log a venue transaction with a bot."
    )
    async def log_transaction(
        self,
        ctx: ApplicationContext,
        amount: Option(
            SlashCommandOptionType.integer,
            name="amount",
            description="The amount of the transaction.",
            required=True,
            max_value=999999999,
        ),
        category: Option(
            SlashCommandOptionType.string,
            name="category",
            description="The category of the transaction.",
            required=True,
            # This line works fine, Intellisense just doesn't like it.
            choices=[OptionChoice(name=opt.label, value=opt.value) for opt in TransactionCategory.select_options()]  # type: ignore
        ),
        memo: Option(
            SlashCommandOptionType.string,
            name="memo",
            description="A memo for the transaction.",
            required=False
        ),
        tags: Option(
            SlashCommandOptionType.string,
            name="tags",
            description="Comma-separated lookup tags for the transaction.",
            required=False
        )
    ) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.finance_manager.record_transaction(ctx.interaction, amount, category, memo, tags)

################################################################################
    @admin.command(
        name="glyph_builder",
        description="Build a PF message interactively."
    )
    async def build_pf_message(self, ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.message_builder.main_menu(ctx.interaction)

################################################################################
def setup(bot: "FroggeBot") -> None:
    
    bot.add_cog(Admin(bot))
                
################################################################################
    