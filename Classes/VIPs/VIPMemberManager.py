from __future__ import annotations

import asyncio
from datetime import timedelta, datetime

from typing import TYPE_CHECKING, Any, List, Optional

from discord import Interaction, User, Embed, EmbedField, Member

from Classes.Common import ObjectManager
from Errors import InvalidNumber
from UI.VIPs import VIPMemberManagerMenuView
from UI.Common import FroggeView, FroggeSelectView, ConfirmCancelView, BasicNumberModal
from .VIPMember import VIPMember
from logger import log
from Utilities import Utilities as U
from Enums import TransactionCategory

if TYPE_CHECKING:
    from Classes import GuildData, VIPTier
################################################################################

__all__ = ("VIPMemberManager", )

################################################################################
class VIPMemberManager(ObjectManager):

    def __init__(self, state: GuildData) -> None:

        super().__init__(state)
    
################################################################################
    @property
    def members(self) -> List[VIPMember]:
        
        return self._managed
    
################################################################################
    def get_member_by_user_id(self, user_id: int) -> Optional[VIPMember]:
        
        return next((member for member in self.members if member._user.id == user_id), None)
    
################################################################################
    async def load_all(self, payload: Any) -> None:

        self._managed = [VIPMember.load(self, member) for member in payload]

################################################################################
    async def status(self) -> Embed:

        tier_dict = {tier.id: 0 for tier in self.guild.vip_manager.tiers}
        for member in self.members:
            tier_dict[member.tier.id] += 1

        field_str = "\n".join([
            f"* **{self.guild.vip_manager.tier_manager[tier_id].name}** - {count} members"  # type: ignore
            for tier_id, count in tier_dict.items()
        ])

        return U.make_embed(
            title="__VIP Member Status__",
            description="Current VIP Tiers and their membership counts:",
            fields=[
                EmbedField(
                    name="** **",
                    value=field_str,
                    inline=False
                )
            ]
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return VIPMemberManagerMenuView(user, self)

################################################################################
    async def add_item(self, interaction: Interaction, user: Optional[User] = None) -> None:
        
        log.info(self.guild, "Adding VIP member...")

        if user is None:
            prompt = U.make_embed(
                title="__Add VIP Member__",
                description="Please mention the user you would like to add as a VIP member."
            )
            
            user = await U.listen_for(interaction, prompt, U.MentionableType.User)
            if user is None:
                log.debug(self.guild, "User cancelled the operation.")
                return
            
        log.info(self.guild, f"Adding VIP member: {user.id}")

        member = self[user.id]  # type: ignore
        if member:
            log.debug(self.guild, f"User {user.id} is already a VIP member.")
            notification = U.make_embed(
                title="__Oops!__",
                description="This user is already a VIP member. Displaying menu..."
            )
            await interaction.respond(embed=notification, delete_after=5)
            await asyncio.sleep(2)
            await member.menu(interaction)
            return

        prompt = U.make_embed(
            title="__Select Membership Tier__",
            description="Please select the membership tier for this new user."
        )
        view = FroggeSelectView(
            owner=interaction.user, 
            options=[t.select_option() for t in self.guild.vip_manager.tiers],
            return_interaction=True
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "User cancelled the operation.")
            return

        tier_id, inter = view.value

        tier: VIPTier = self.guild.vip_manager.tier_manager[tier_id]  # type: ignore

        end_date = None
        if not tier.lifetime:
            modal = BasicNumberModal(
                title="Enter Membership Days",
                attribute="Days",
                example="eg. 30",
                cur_val=30,
                max_length=3,
            )

            await inter.response.send_modal(modal)
            await modal.wait()

            if not modal.complete:
                return

            try:
                parsed = int(modal.value)
            except ValueError:
                log.error(self.guild, "Invalid number entered for membership days.")
                error = InvalidNumber(modal.value)
                await interaction.respond(embed=error)
                return

            end_date = datetime.now() + timedelta(days=parsed)

        member = VIPMember.new(self, user, tier, end_date)
        self.members.append(member)
        
        log.info(self.guild, f"VIP member added: {user.id}")
        await self.guild.vip_manager.update_post_components()

        # Generate VIP Transaction
        if tier.cost:
            await self.guild.finance_manager.record_transaction(
                interaction=interaction,
                amount=tier.cost,
                category=TransactionCategory.VIP,
                memo=f"VIP Membership: {tier.name}",
                tags=[]
            )

        await member.menu(interaction)

################################################################################
    async def modify_item(self, interaction: Interaction) -> None:
        
        log.info(self.guild, "Modifying VIP member...")

        prompt = U.make_embed(
            title="__Modify VIP Member__",
            description=(
                "Please mention the user you would like to modify the "
                "VIP membership for."
            )
        )

        user = await U.listen_for(interaction, prompt, U.MentionableType.User)
        if user is None:
            log.debug(self.guild, "User cancelled the operation.")
            return
        
        log.info(self.guild, f"Modifying VIP member: {user.id}")

        await self.member_status(interaction, user)  # type: ignore

################################################################################
    async def remove_item(self, interaction: Interaction) -> None:
        
        log.info(self.guild, "Removing VIP member...")

        prompt = U.make_embed(
            title="__Remove VIP Member__",
            description=(
                "Please mention the user you would like to remove from the "
                "VIP membership list.\n\n"

                "__**PLEASE NOTE:**__ This will completely delete all VIP "
                "data for the user and is irreversible."
            )
        )

        user = await U.listen_for(interaction, prompt, U.MentionableType.User)
        if user is None:
            log.debug(self.guild, "User cancelled the operation.")
            return

        member = self.get_member_by_user_id(user.id)
        
        log.info(self.guild, f"Removing VIP member: {user.id}")

        confirm = U.make_embed(
            title="__Confirm Removal__",
            description=(
                f"Are you sure you want to remove {user.mention} from the VIP "
                "membership list? This action is irreversible."
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "User cancelled the operation.")
            return

        member.delete()
        await self.guild.vip_manager.update_post_components()
        
        log.info(self.guild, f"VIP member removed: {user.id}")

        confirmation = U.make_embed(
            title="__Success!__",
            description=f"{user.mention} has been removed from the VIP membership list."
        )
        await interaction.respond(embed=confirmation)
    
################################################################################
    async def member_status(self, interaction: Interaction, user: Member) -> None:

        if member := self.get_member_by_user_id(user.id):
            await member.menu(interaction)
            return

        confirm = U.make_embed(
            title="__Member Not Found__",
            description=(
                f"{user.mention} is not a VIP member. Would you like to add them?"
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        prompt = U.make_embed(
            title="__Select Membership Tier__",
            description="Please select the membership tier for this new user."
        )
        view = FroggeSelectView(interaction.user, [t.select_option() for t in self.guild.vip_manager.tiers])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        tier = self.guild.vip_manager.tier_manager[view.value]
        member = VIPMember.new(self, user, tier)  # type: ignore
        self.members.append(member)

        await member.menu(interaction)

################################################################################
        