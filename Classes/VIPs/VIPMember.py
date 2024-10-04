from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional, List, Type, TypeVar, Any, Dict

from discord import User, Embed, Interaction, Forbidden, NotFound

from Classes.Common import ManagedObject, LazyUser
from Enums import RedemptionLevel
from Errors import UserMissing, RoleMissing, InsufficientPermissions, DateBeforeNow
from UI.Common import (
    FroggeView,
    FroggeSelectView,
    ConfirmCancelView,
    DateTimeModal,
    BasicTextModal,
    BasicNumberModal,
    InstructionsInfo
)
from UI.VIPs import VIPMemberStatusView
from Utilities import Utilities as U
from .VIPPerkOverride import VIPPerkOverride

if TYPE_CHECKING:
    from Classes import VIPMemberManager, VIPTier, VIPPerk
################################################################################

__all__ = ("VIPMember", )

VM = TypeVar("VM", bound="VIPMember")

################################################################################
class VIPMember(ManagedObject):

    __slots__ = (
        "_tier",
        "_user",
        "_join_date",
        "_expiry_date",
        "_overrides",
        "_notes"
    )
    
################################################################################
    def __init__(self, mgr: VIPMemberManager, _id: int, **kwargs) -> None:

        super().__init__(mgr, _id)
        
        self._tier: VIPTier = kwargs.pop("tier")
        self._user: LazyUser = LazyUser(self, kwargs.pop("user_id"))
        self._notes: Optional[str] = kwargs.get("notes")
        
        self._join_date: datetime = kwargs.pop("join_date")
        self._expiry_date: Optional[datetime] = kwargs.get("expiry_date")
        
        self._overrides: List[VIPPerkOverride] = kwargs.get("overrides", [])
    
################################################################################
    @classmethod
    def new(cls: Type[VM], mgr: VIPMemberManager, user: User, tier: VIPTier, end_date: Optional[datetime]) -> VM:

        new_member = mgr.bot.api.create_vip_member(mgr.guild_id, user.id, tier.id, end_date)
        return cls(
            mgr=mgr,
            _id=new_member["id"],
            tier=tier,
            user_id=user.id,
            join_date=datetime.fromisoformat(new_member["join_date"]),
            expiry_date=datetime.fromisoformat(new_member["expiry_date"]) if new_member["expiry_date"] else None,
        )
    
################################################################################
    @classmethod
    def load(cls: Type[VM], mgr: VIPMemberManager, data: Dict[str, Any]) -> VM:
        
        self: VM = cls.__new__(cls)
        
        self._mgr = mgr
        self._id = data["id"]
        
        self._tier = mgr._state.vip_manager.tier_manager[data["tier_id"]]
        self._user = LazyUser(self, data["user_id"])
        self._notes = data["notes"]
        
        self._join_date = datetime.fromisoformat(data["join_date"])
        self._expiry_date = datetime.fromisoformat(data["expiry_date"]) if data["expiry_date"] else None
        
        self._overrides = [VIPPerkOverride.load(self, override) for override in data["overrides"]]
        
        return self
    
################################################################################
    @property
    def tier(self) -> VIPTier:
        
        return self._tier
    
    @tier.setter
    def tier(self, value: VIPTier) -> None:
        
        self._tier = value
        self.update()
        
################################################################################
    @property
    async def user(self) -> User:
        
        return await self._user.get()
    
################################################################################
    @property
    def join_date(self) -> datetime:
        
        return self._join_date
    
    @join_date.setter
    def join_date(self, value: datetime) -> None:
        
        self._join_date = value
        self.update()
        
################################################################################
    @property
    def end_date(self) -> Optional[datetime]:
        
        return self._expiry_date
    
    @end_date.setter
    def end_date(self, value: Optional[datetime]) -> None:
        
        self._expiry_date = value
        self.update()
        
################################################################################
    @property
    def overrides(self) -> List[VIPPerkOverride]:
        
        return self._overrides
    
################################################################################
    @property
    def notes(self) -> Optional[str]:
        
        return self._notes
    
    @notes.setter
    def notes(self, value: Optional[str]) -> None:
        
        self._notes = value
        self.update()
        
################################################################################
    @property
    def is_lifetime(self) -> bool:
        
        return self._tier.lifetime
        
################################################################################
    def update(self) -> None:
        
        self.bot.api.update_vip_member(self)
        
################################################################################
    def to_dict(self) -> Dict[str, Any]:
        
        return {
            "tier_id": self._tier.id,
            "join_date": self._join_date.isoformat(),
            "expiry_date": self._expiry_date.isoformat() if self._expiry_date else None,
            "notes": self._notes,
        }
        
################################################################################
    def delete(self) -> None:

        self.bot.api.delete_vip_member(self.id)
        self._mgr._managed.remove(self)

################################################################################
    async def status(self) -> Embed:

        fully_redeemed = [o for o in self.overrides if o.level == RedemptionLevel.FullyRedeemed]
        user = await self.user
        return U.make_embed(
            title=f"__VIP Status: `{user.display_name}`__",
            description=(
                f"**Tier:** `{self.tier.name}`\n"
                f"**Join Date:** {U.format_dt(self.join_date, 'D')}\n"
                f"**End Date:** {U.format_dt(self.end_date, 'D') if self.end_date else '`Lifetime`'}\n"
                f"**Perk Redemptions:** [`{len(fully_redeemed)}/{len(self.tier.perks)}`]\n"
                f"**Notes:**\n```{self.notes or 'None'}```"
            )
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:
        
        return VIPMemberStatusView(user, self)
    
################################################################################
    async def set_tier(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set VIP Tier__",
            description=(
                "Please select the new VIP Tier for this member."
            )
        )
        view = FroggeSelectView(
            owner=interaction.user,
            options=[t.select_option() for t in self.guild.vip_manager.tier_manager.tiers]
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        new_tier: VIPTier = self.guild.vip_manager.tier_manager[int(view.value)]  # type: ignore
        old_tier = self.tier

        if self.tier.lifetime and not new_tier.lifetime:
            confirm = U.make_embed(
                title="__Lifetime VIP Warning__",
                description=(
                    "You are attempting to downgrade this **lifetime** VIP to "
                    "a **non-lifetime** tier.\n\n"

                    "Are you sure you want to continue?"
                )
            )
            view = ConfirmCancelView(interaction.user, return_interaction=True)

            await interaction.respond(embed=confirm, view=view)
            await view.wait()

            if not view.complete or view.value[0] is False:
                return

            _, inter = view.value
            await self.set_end_date(inter)
        elif new_tier.lifetime and not self.tier.lifetime:
            confirm = U.make_embed(
                title="__Lifetime VIP Warning__",
                description=(
                    "You are attempting to upgrade this VIP to a **lifetime** tier.\n\n"

                    "Are you sure you want to continue?"
                )
            )
            view = ConfirmCancelView(interaction.user, return_interaction=True)

            await interaction.respond(embed=confirm, view=view)
            await view.wait()

            if not view.complete or view.value[0] is False:
                return

            _, inter = view.value
            self.end_date = None

        user = await self.user
        if user is None:
            error = UserMissing(self._user.id)
            await interaction.respond(embed=error, ephemeral=True)
            return

        error = None

        user = await self.user
        if new_tier._role.id is not None:
            role = await new_tier.role
            try:
                await user.add_roles(role, reason="VIP Tier Change")  # type: ignore
            except Forbidden:
                error = InsufficientPermissions(None, "Add Roles")
            except NotFound:
                error = RoleMissing(role.name)

        if error is not None:
            await interaction.respond(embed=error, ephemeral=True)
            return

        if old_tier._role.id is not None:
            role = await old_tier.role
            try:
                await user.remove_roles(role, reason="VIP Tier Change")  # type: ignore
            except Forbidden:
                error = InsufficientPermissions(None, "Remove Roles")
            except NotFound:
                error = RoleMissing(role.name)

        if error is not None:
            await interaction.respond(embed=error, ephemeral=True)
            return

        self.tier = new_tier
        await self.guild.vip_manager.update_post_components()

################################################################################
    async def set_end_date(self, interaction: Interaction) -> None:

        modal = DateTimeModal(
            "VIP Membership End Date",
            current_dt=self.py_tz.localize(self.end_date) if self.end_date else None
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        if modal.value.date() < self.py_tz.localize(datetime.now()).date():
            error = DateBeforeNow(modal.value)
            await interaction.respond(embed=error, ephemeral=True)
            return

        self.end_date = self.py_tz.localize(modal.value)

################################################################################
    async def set_notes(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="VIP Member Notes",
            attribute="Notes",
            cur_val=self.notes,
            max_length=500,
            required=False,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.notes = modal.value

################################################################################
    async def modify_perk_redemptions(self, interaction: Interaction) -> None:

        options = []
        for perk in self.tier.perks:
            option = perk.select_option()
            for override in self.overrides:
                if override.perk.id == perk.id:
                    option.description = f"({override.level.proper_name})"
                    break
            options.append(option)

        prompt = U.make_embed(
            title="__Modify Perk Redemptions__",
            description=(
                "Please select the perk to modify..."
            )
        )
        view = FroggeSelectView(
            owner=interaction.user,
            options=options,
            multi_select=True,
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        perks = [self.tier.get_perk(int(p)) for p in view.value]

        prompt2 = U.make_embed(
            title="__Select Perk Level__",
            description=(
                "Please select the new redemption level for the selected perk(s)..."
            )
        )
        view = FroggeSelectView(interaction.user, RedemptionLevel.select_options())

        await interaction.respond(embed=prompt2, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        level = RedemptionLevel(int(view.value))

        for p in perks:
            self.add_override(p, level)

################################################################################
    def clear_overrides(self) -> None:

        for override in self.overrides:
            override.delete()

################################################################################
    def add_override(self, perk: VIPPerk, level: RedemptionLevel) -> None:

        for override in self.overrides:
            if override.perk.id == perk.id:
                override.level = level
                return

        override = VIPPerkOverride.new(self, perk, level)
        self.overrides.append(override)

################################################################################
    async def add_membership(self, interaction: Interaction) -> None:

        if self.tier.lifetime:
            await interaction.respond(
                "Lifetime VIPs do not have an end date. Quitting Operation.",
                delete_after=5
            )
            return

        assert self.end_date is not None, "End date should be set for non-lifetime VIPs."

        modal = BasicNumberModal(
            title="Add VIP Membership",
            attribute="Num. Days",
            example="e.g. '69'",
            required=True,
            instructions=InstructionsInfo(
                placeholder="Enter a number of days to add or subtract from the VIP Membership.",
                value="Enter the number of days to add or subtract from the VIP Membership."
            )
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        proposed_end_date = self.end_date + timedelta(days=modal.value)

        if proposed_end_date.date() < datetime.now().date():
            error = DateBeforeNow(proposed_end_date.strftime("%m/%d/%y"))
            await interaction.respond(embed=error, ephemeral=True)
            return

        self.end_date = proposed_end_date

################################################################################
    async def remove(self, interaction: Interaction) -> None:

        user = await self.user
        confirm = U.make_embed(
            title="__Remove VIP Membership__",
            description=(
                f"Are you sure you want to remove {user.mention} from the VIP "
                "membership list? This action is irreversible."
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        confirm = U.make_embed(
            title="__VIP Membership Removed__",
            description=(
                f"{user.mention} has been removed from the VIP membership list."
            )
        )
        await interaction.respond(embed=confirm)

        self.delete()

################################################################################
