from __future__ import annotations

from typing import TYPE_CHECKING, List, Any, Dict, Optional

from discord import (
    Message,
    Embed,
    EmbedField,
    Interaction,
    Member,
    Forbidden,
    NotFound,
    SelectOption,
    User,
)

from Assets import BotEmojis
from Enums import VIPMessageType
from Utilities import Utilities as U, FroggeColor
from Utilities.Constants import DEFAULT_VIP_WARNING_DAYS
from .VIPMemberManager import VIPMemberManager
from .VIPMessage import VIPMessage
from UI.VIPs import VIPManagerMenuView, VIPMessageManagementView
from .VIPTierManager import VIPTierManager
from UI.Common import FroggeSelectView, ConfirmCancelView
from Errors import InsufficientPermissions
from Classes.Common import LazyMessage

if TYPE_CHECKING:
    from Classes import GuildData, FroggeBot, VIPTier, VIPMember, VIPPerk
################################################################################

__all__ = ("VIPManager", )

################################################################################
class VIPManager:

    __slots__ = (
        "_state",
        "_tier_mgr",
        "_member_mgr",
        "_warning_msg",
        "_expiry_msg",
        "_warning_threshold",
        "_post_msgs",
        "_perks_msgs",
    )
    
################################################################################
    def __init__(self, state: GuildData) -> None:

        self._state: GuildData = state
        
        self._tier_mgr: VIPTierManager = VIPTierManager(state)
        self._member_mgr: VIPMemberManager = VIPMemberManager(state)
        
        self._warning_msg: VIPMessage = VIPMessage(self, VIPMessageType.Warning)
        self._expiry_msg: VIPMessage = VIPMessage(self, VIPMessageType.Expiry)
        
        self._warning_threshold: int = DEFAULT_VIP_WARNING_DAYS
        
        self._post_msgs: List[LazyMessage] = []
        self._perks_msgs: List[LazyMessage] = []
    
################################################################################
    async def load_all(self, data: Dict[str, Any]) -> None:
        
        await self._tier_mgr.load_all(data["tiers"])
        await self._member_mgr.load_all(data["members"])
        
        self._warning_threshold = data.get("warning_threshold", DEFAULT_VIP_WARNING_DAYS)
        
        self._post_msgs = [LazyMessage(self, url) for url in data.get("post_urls", [])]
        self._perks_msgs = [LazyMessage(self, url) for url in data.get("perks_urls", [])]
        
        for message in data["messages"]:
            if message["message_type"] == 1:
                self._warning_msg = VIPMessage.load(self, message)
            elif message["message_type"] == 2:
                self._expiry_msg = VIPMessage.load(self, message)
                
################################################################################
    def __getitem__(self, item_id: int) -> Optional[VIPMember]:

        return next((member for member in self.members if member.id == int(item_id)), None)

################################################################################
    @property
    def bot(self) -> FroggeBot:
        
        return self._state.bot
    
################################################################################
    @property
    def guild(self) -> GuildData:
        
        return self._state
    
################################################################################
    @property
    def tier_manager(self) -> VIPTierManager:
        
        return self._tier_mgr
    
    @property
    def tiers(self) -> List[VIPTier]:
        
        return self._tier_mgr.tiers
    
################################################################################
    @property
    def member_manager(self) -> VIPMemberManager:
        
        return self._member_mgr
    
    @property
    def members(self) -> List[VIPMember]:
        
        return self._member_mgr.members
    
################################################################################
    @property
    def warning_threshold(self) -> int:
        
        return self._warning_threshold
    
    @warning_threshold.setter
    def warning_threshold(self, value: int) -> None:
        
        self._warning_threshold = value
        self.update()
        
################################################################################
    @property
    def warning_message(self) -> VIPMessage:
        
        return self._warning_msg
    
################################################################################
    @property
    def expiry_message(self) -> VIPMessage:
        
        return self._expiry_msg
    
################################################################################
    @property
    def regular_vips(self) -> List[VIPMember]:
        
        return [member for member in self.members if not member.is_lifetime]
    
    @property
    def lifetime_vips(self) -> List[VIPMember]:
        
        return [member for member in self.members if member.is_lifetime]
    
################################################################################
    def update(self) -> None:
        
        self._state.bot.api.update_vip_program(self)
        
################################################################################
    def to_dict(self) -> Dict[str, Any]:
        
        return {
            "warning_threshold": self._warning_threshold,
            "post_urls": [msg.id for msg in self._post_msgs],
            "perks_urls": [msg.id for msg in self._perks_msgs],
        }
    
################################################################################
    @property
    async def post_messages(self) -> List[Message]:

        return [await m.get() for m in self._post_msgs]

################################################################################
    @property
    async def perks_messages(self) -> List[Message]:

        return [await m.get() for m in self._perks_msgs]

################################################################################
    def status(self) -> Embed:

        return U.make_embed(
            title="__VIP Program Status Overview__",
            fields=[
                EmbedField(
                    name="__**Tiers**__",
                    value=(
                        "\n".join(f"* `{tier.name}`" for tier in self.tiers)
                    ) if self.tiers else "`No Tiers Defined`",
                    inline=True
                ),
                EmbedField(
                    name="__**Members**__",
                    value=(
                        f"**[`{len(self.lifetime_vips)}`]** - Lifetime VIPs\n"
                        f"**[`{len(self.regular_vips)}`]** - Regular VIPs"
                    )
                )
            ]
        )
    
################################################################################
    async def compile(self) -> List[Embed]:

        embeds = []
        for tier in self.tiers:
            member_str = ""
            for member in tier.members:
                user = await member.user
                if user is None:
                    continue
                member_str = f"{user.display_name} - {user.mention}"
            embed = U.make_embed(
                color=tier.color or FroggeColor.embed_background(),
                title=f"__`{tier.name}`__",
                description="*(Lifetime)*" if tier.lifetime else None,
                fields=[
                    EmbedField(
                        name="** **",
                        value=member_str,
                        inline=True
                    )
                ]
            )
            embeds.append(embed)

        return embeds
    
################################################################################
    def perks_compile(self) -> Embed:

        return U.make_embed(
            title="__VIP Packages__",
            fields=[
                EmbedField(
                    name=f"__{tier.name or 'Unnamed Tier'}__",
                    value=(
                        f"**Cost:** {U.abbreviate_number(tier.cost)} "
                        f"{' / month' if not tier.lifetime else ''}\n"
                        "**Perks:**\n" + "\n".join(
                            f"{BotEmojis.Diamond} -- {perk.text}"
                            for perk in tier.perks
                        )
                    ),
                    inline=False
                )
                for tier in self.tiers
            ]
        )

################################################################################
    async def main_menu(self, interaction: Interaction) -> None:

        embed = self.status()
        view = VIPManagerMenuView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def tier_management(self, interaction: Interaction) -> None:

        await self._tier_mgr.main_menu(interaction)

################################################################################
    async def member_management(self, interaction: Interaction, member: Optional[Member] = None) -> None:

        if member is not None:
            await self._member_mgr.member_status(interaction, member)
            return

        await self._member_mgr.main_menu(interaction)

################################################################################
    async def update_post_components(self) -> bool:

        if not self._post_msgs:
            return False

        for message in self._post_msgs:
            try:
                embeds = await self.compile()
                msg = await message.get()
                await msg.edit(embeds=embeds)
            except Forbidden:
                continue
            except NotFound:
                self._post_msgs.remove(message)
                self.update()
                
################################################################################
    async def update_perks_post_components(self) -> bool:

        if not self._perks_msgs:
            return False

        for message in self._perks_msgs:
            try:
                embed = self.perks_compile()
                msg = await message.get()
                await msg.edit(embed=embed)
            except Forbidden:
                continue
            except NotFound:
                self._perks_msgs.remove(message)
                self.update()

################################################################################
    def get_perk(self, perk_id: int) -> Optional[VIPPerk]:

        for tier in self.tiers:
            for perk in tier.perks:
                if perk.id == perk_id:
                    return perk

################################################################################
    async def message_management(self, interaction: Interaction) -> None:

        embed = U.make_embed(
            title="__VIP Message Management__",
            description=(
                "Please select a button below to manage the VIP Expiry Message "
                "or the VIP Warning Message."
            )
        )
        view = VIPMessageManagementView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def warning_message_management(self, interaction: Interaction) -> None:

        await self._warning_msg.main_menu(interaction)

################################################################################    
    async def expiry_message_management(self, interaction: Interaction) -> None:

        await self._expiry_msg.main_menu(interaction)

################################################################################
    async def set_warning_threshold(self, interaction: Interaction) -> None:

        options = [SelectOption(label="No Reminders", value="-2")]  # Must be -2 to avoid disabling the select menu
        options.extend([
            SelectOption(label=f"{str(i)} Days", value=str(i))
            for i in range(1, 8)
        ])

        prompt = U.make_embed(
            title="Adjust Warning Threshold",
            description=(
                "Please select the number of days before a VIP Membership "
                "expires that the warning message should be sent."
            )
        )
        view = FroggeSelectView(interaction.user, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        raw_value = int(view.value)

        self.warning_threshold = raw_value if raw_value > 0 else None

################################################################################
    async def post_vip_list(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Post VIP List__",
            description=(
                "Please enter a mention of the channel where you would like "
                "the VIP List to be posted."
            )
        )
        channel = await U.select_channel(interaction, self.guild, "VIP List Channel", prompt)
        if channel is not None:
            try:
                post_message = await channel.send(embeds=await self.compile())
            except Forbidden:
                error = InsufficientPermissions(channel, "Send Messages")
                await interaction.respond(embed=error, ephemeral=True)
                return
            else:
                self._post_msgs.append(LazyMessage(self, post_message.jump_url))
                self.update()

################################################################################
    async def post_vip_perks_message(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Post VIP Perks Message__",
            description=(
                "Please enter a mention of the channel where you would like "
                "the VIP Perks List message to be posted."
            )
        )
        channel = await U.select_channel(interaction, self.guild, "VIP Perks Channel", prompt)
        if channel is not None:
            try:
                post_message = await channel.send(embed=self.perks_compile())
            except Forbidden:
                error = InsufficientPermissions(channel, "Send Messages")
                await interaction.respond(embed=error, ephemeral=True)
                return
            else:
                self._perks_msgs.append(LazyMessage(self, post_message.jump_url))
                self.update()

################################################################################
    async def vip_member_menu_ctx(self, interaction: Interaction, user: User) -> None:

        if member := self[user.id]:
            await member.menu(interaction)
            return

        prompt = U.make_embed(
            title="__Add VIP Member__",
            description=(
                f"Would you like to add {user.mention} ({user.display_name}) "
                f"as a VIP Member?"
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        await self._member_mgr.add_item(interaction, user)

################################################################################
