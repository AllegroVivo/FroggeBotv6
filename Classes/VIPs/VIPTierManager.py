from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

from discord import Interaction, User, Embed, EmbedField

from Classes.Common import ObjectManager
from UI.Common import FroggeView, FroggeSelectView, ConfirmCancelView
from .VIPTier import VIPTier
from UI.VIPs import VIPTierManagerMenuView
from Utilities import Utilities as U
from logger import log

if TYPE_CHECKING:
    from Classes import GuildData
################################################################################

__all__ = ("VIPTierManager", )

################################################################################
class VIPTierManager(ObjectManager):

    MAX_ITEMS = 10
    
################################################################################
    def __init__(self, state: GuildData) -> None:

        super().__init__(state)
    
################################################################################
    @property
    def tiers(self) -> List[VIPTier]:
        
        return self._managed  # type: ignore
    
################################################################################
    async def load_all(self, payload: Any) -> None:
        
        self._managed = [VIPTier.load(self, tier) for tier in payload]

################################################################################
    async def status(self) -> Embed:

        fields = []
        for tier in self.tiers:
            cost = f"`{tier.cost:,} gil`" if tier.cost is not None else "`Not Set`"
            role = await tier.role
            fields.append(
                EmbedField(
                    name=tier.name if tier.name else "Unnamed Tier",
                    value=(
                        f"Cost: {cost}\n"
                        f"Role: {role.mention if role else '`Not Set`'}\n"
                        f"Perks: [`{len(tier.perks)}`]"
                    ),
                    inline=True
                )
            )

        return U.make_embed(
            title="__VIP Tiers Status__",
            description="Current VIP Tiers and their costs:",
            fields=fields
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:
        
        return VIPTierManagerMenuView(user, self)

################################################################################
    async def add_item(self, interaction: Interaction) -> None:
        
        log.info(self.guild, "Adding VIP Tier...")

        if len(self.tiers) >= self.MAX_ITEMS:
            error = U.make_error(
                title="Max VIP Tiers Reached",
                description=f"**Maximum Tier Count:** `{self.MAX_ITEMS}`",
                message="You have reached the maximum number of VIP Tiers allowed.",
                solution=(
                    "You cannot create any more VIP Tiers. "
                    "If you wish to add more, you must delete an existing one."
                )
            )
            await interaction.respond(embed=error, ephemeral=True)
            log.debug(self.guild, "Max VIP Tiers reached.")
            return

        tier = VIPTier.new(mgr=self)
        self.tiers.append(tier)
        
        log.info(self.guild, f"VIP Tier added (ID: {tier.id})")

        await tier.menu(interaction)

################################################################################
    async def modify_item(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Modifying VIP Tier for guild: {self.guild_id}...")

        prompt = U.make_embed(
            title="__Modify VIP Tier__",
            description="Please select the position you would like to modify."
        )
        view = FroggeSelectView(interaction.user, [p.select_option() for p in self.tiers])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "VIP Tier modification cancelled.")
            return

        tier = self[view.value]
        await tier.menu(interaction)

################################################################################
    async def remove_item(self, interaction: Interaction) -> None:

        log.info(self.guild, "Removing VIP Tier...")

        prompt = U.make_embed(
            title="__Remove VIP Tier__",
            description="Please select the tier you would like to remove."
        )
        view = FroggeSelectView(interaction.user, [p.select_option() for p in self.tiers])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "VIP Tier removal cancelled.")
            return

        tier = self[view.value]
        await tier.remove(interaction)
    
################################################################################
    async def bulk_move_tier(self, interaction: Interaction) -> None:

        # TODO: Update this prompt with better wording.
        confirm = U.make_embed(
            title="Bulk Move Tier",
            description=(
                "Are you sure you want to bulk move all members from one VIP "
                "Tier to another?\n\n"

                "This will have the following effects:\n"
                "```... ... ...```"
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        tier_options = [t.select_option() for t in self.tiers]
        prompt = U.make_embed(
            title="Bulk Transfer Tier",
            description="Select the VIP Tier you would like to transfer all members __**FROM**__."
        )
        view = FroggeSelectView(interaction.user, tier_options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is None:
            return

        from_tier = self[view.value]
        tier_options2 = [t.select_option() for t in self.tiers if t != from_tier]

        prompt = U.make_embed(
            title="Bulk Transfer Tier",
            description="Select the VIP Tier you would like to transfer all members __**TO**__."
        )
        view = FroggeSelectView(interaction.user, tier_options2)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is None:
            return

        to_tier = self[view.value]

        confirm = U.make_embed(
            title="Confirm Bulk Transfer",
            description=(
                f"Are you sure you want to bulk transfer all `{len(from_tier.members)}` "  # type: ignore
                f"members from the VIP Tier `{from_tier.name}` to the VIP Tier `{to_tier.name}`?"  # type: ignore
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        inter = await interaction.respond("Processing Bulk Transfer, Please Wait...")

        await self.guild.log.bulk_tier_reassignment(from_tier.members, to_tier)  # type: ignore

        for member in from_tier.members:  # type: ignore
            member.tier = to_tier

        await inter.delete()

        confirm = U.make_embed(
            title="Bulk Transfer Complete",
            description=(
                f"`{len(from_tier.members)}` members have been successfully transferred "  # type: ignore
                f"from the VIP Tier `{from_tier.name}` to the VIP Tier `{to_tier.name}`."  # type: ignore
            )
        )
        await interaction.respond(embed=confirm)
        
################################################################################
