from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar, Any, Dict, List

from discord import User, Embed, SelectOption, EmbedField, Interaction, Role

from Assets import BotEmojis
from Classes.Common import ManagedObject, LazyRole
from Errors import InvalidMonetaryAmount
from UI.Common import BasicTextModal, FroggeSelectView, ConfirmCancelView, AccentColorModal
from UI.VIPs import VIPTierStatusView
from Utilities import Utilities as U, FroggeColor
from .VIPPerksManager import VIPPerksManager

if TYPE_CHECKING:
    from Classes import VIPTierManager, VIPPerk, VIPMember
    from UI.Common import FroggeView
################################################################################

__all__ = ("VIPTier", )

VT = TypeVar("VT", bound="VIPTier")

################################################################################
class VIPTier(ManagedObject):

    __slots__ = (
        "_name",
        "_cost",
        "_perks",
        "_role",
        "_lifetime",
        "_order",
        "_color",
        "_thumbnail"
    )
    
################################################################################
    def __init__(self, mgr: VIPTierManager, _id: int, **kwargs) -> None:

        super().__init__(mgr, _id)
        
        self._name: Optional[str] = kwargs.get("name")
        self._cost: Optional[int] = kwargs.get("cost")
        self._role: LazyRole = LazyRole(self, kwargs.get("role_id"))
        self._lifetime: bool = kwargs.get("lifetime", False)
        
        self._order: int = kwargs.get("order", 0)
        self._color: Optional[FroggeColor] = kwargs.get("color")
        self._thumbnail: Optional[str] = kwargs.get("thumbnail")
        
        self._perks: VIPPerksManager = kwargs.get("perks", None) or VIPPerksManager(self)
    
################################################################################
    @classmethod
    def new(cls: Type[VT], mgr: VIPTierManager) -> VT:

        new_tier = mgr.bot.api.create_vip_tier(mgr.guild.guild_id)
        return cls(mgr, new_tier["id"])
        
################################################################################
    @classmethod
    def load(cls: Type[VT], mgr: VIPTierManager, data: Dict[str, Any]) -> VT:
        
        self: VT = cls.__new__(cls)
        
        self._mgr = mgr
        self._id = data["id"]
        
        self._name = data["name"]
        self._cost = data["cost"]
        self._role = LazyRole(self, data["role_id"])
        self._lifetime = data["lifetime"]
        
        self._order = data["sort_order"]
        self._color = FroggeColor(data["color"]) if data["color"] else None
        self._thumbnail = data["thumbnail_url"]
        
        self._perks = VIPPerksManager.load(self, data["perks"])
        
        return self

################################################################################
    @property
    def name(self) -> str:
        
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        
        self._name = value
        self.update()
        
################################################################################
    @property
    def cost(self) -> int:
        
        return self._cost
    
    @cost.setter
    def cost(self, value: int) -> None:
        
        self._cost = value
        self.update()
        
################################################################################
    @property
    async def role(self) -> Role:
        
        return await self._role.get()
    
    @role.setter
    def role(self, value: Role) -> None:

        self._role.set(value)
        
################################################################################
    @property
    def lifetime(self) -> bool:
        
        return self._lifetime
    
    @lifetime.setter
    def lifetime(self, value: bool) -> None:
        
        self._lifetime = value
        self.update()
        
################################################################################
    @property
    def order(self) -> int:
        
        return self._order
    
    @order.setter
    def order(self, value: int) -> None:
        
        self._order = value
        self.update()
        
################################################################################
    @property
    def color(self) -> FroggeColor:
        
        return self._color
    
    @color.setter
    def color(self, value: FroggeColor) -> None:
        
        self._color = value
        self.update()
        
################################################################################
    @property
    def thumbnail(self) -> str:
        
        return self._thumbnail
    
    @thumbnail.setter
    def thumbnail(self, value: str) -> None:
        
        self._thumbnail = value
        self.update()
        
################################################################################
    @property
    def perks_manager(self) -> VIPPerksManager:
        
        return self._perks
    
    @property
    def perks(self) -> List[VIPPerk]:
        
        return self._perks.perks
    
################################################################################
    @property
    def members(self) -> List[VIPMember]:
        
        return [m for m in self.guild.vip_manager.members if m.tier == self]
    
################################################################################
    def update(self) -> None:
        
        self.bot.api.update_vip_tier(self)
        
################################################################################
    def delete(self) -> None:
        
        self.bot.api.delete_vip_tier(self)
        self._mgr.tiers.remove(self)  # type: ignore
        
################################################################################
    def to_dict(self) -> Dict[str, Any]:
        
        return {
            "name": self.name,
            "cost": self.cost,
            "role_id": self._role.id,
            "lifetime": self.lifetime,
            "sort_order": self.order,
            "color": self.color.value if self.color else None,
            "thumbnail_url": self.thumbnail,
        }
    
################################################################################
    async def status(self) -> Embed:

        lifetime_emoji = BotEmojis.Check if self.lifetime else BotEmojis.Cross
        cost = f"`{self.cost:,} gil`" if self.cost is not None else "`Not Set`"
        role = await self.role

        return U.make_embed(
            color=self.color or FroggeColor.embed_background(),
            title=f"Tier: `{self.name}`",
            description=(
                f"**Role:** {role.mention if role else '`Not Set`'}\n"
                f"**Cost:** {cost}\n"
                f"**Lifetime:** {str(lifetime_emoji)}"
            ),
            fields=[
                EmbedField(
                    name="__Accent Color__",
                    value=(
                        f"{BotEmojis.ArrowLeft} -- (__{str(self.color).upper()}__)"
                        if self.color is not None
                        else "`Not Set`"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__Display Order__",
                    value=f"`{self.order}`",
                    inline=True
                ),
                EmbedField(
                    name="__Perks__",
                    value="\n".join(
                        f"**{p.text}** - {p.description}"
                        for p in self.perks
                    ) or "`No Perks`",
                    inline=False
                )
            ],
            thumbnail_url=self.thumbnail
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:
        
        return VIPTierStatusView(user, self)
    
################################################################################
    def select_option(self) -> SelectOption:
        
        return SelectOption(
            label=self.name or "Unnamed Tier",
            value=str(self.id),
            description=f"(Tier {self.order})",
        )
    
################################################################################
    async def set_name(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="VIP Tier Name",
            attribute="Name",
            cur_val=self.name,
            example="e.g. 'Pad Leaper'",
            max_length=40
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        old_name = self.name
        self.name = modal.value

        confirm = U.make_embed(
            title="Name Updated",
            description=(
                f"Tier `{old_name}` has been renamed to `{self.name}`.\n\n"

                "Would you like to update any existing VIP List messages to "
                "reflect the new change?"
            )
        )
        await self._confirm_update_post_components(interaction, confirm)

################################################################################
    async def set_cost(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="VIP Tier Cost",
            attribute="Cost",
            cur_val=f"{self.cost:,}" if self.cost is not None else None,
            example="e.g. '1.5m or 500,000'",
            max_length=11,
            required=False,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        raw_cost = modal.value
        parsed = U.parse_salary(raw_cost)

        if parsed is None:
            error = InvalidMonetaryAmount(raw_cost)
            await interaction.respond(embed=error, ephemeral=True)
            return

        self.cost = parsed

################################################################################
    async def set_role(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="Set Role",
            description="Enter the role you would like to associate with this VIP Tier."
        )
        if role := await U.listen_for(interaction, prompt, U.MentionableType.Role):
            self.role = role

################################################################################
    async def toggle_lifetime(self, interaction: Interaction) -> None:

        self.lifetime = not self.lifetime
        await interaction.respond("** **", delete_after=0.1)

################################################################################
    async def add_perk(self, interaction: Interaction) -> None:

        await self._perks.add_perk(interaction)

################################################################################
    async def modify_perk(self, interaction: Interaction) -> None:

        await self._perks.modify_perk(interaction)

################################################################################
    async def remove_perk(self, interaction: Interaction) -> None:

        await self._perks.remove_perk(interaction)

################################################################################
    def get_perk(self, perk_id: int) -> Optional[VIPPerk]:

        return self._perks[perk_id]

################################################################################
    async def set_color(self, interaction: Interaction) -> None:

        modal = AccentColorModal(self.color)

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.color = modal.value

        confirm = U.make_embed(
            title="Color Updated",
            description=(
                f"Tier `{self.name}`'s accent color has been set to `#{str(self.color)}`.\n\n"

                "Would you like to update any existing VIP List messages to "
                "reflect the new change?"
            )
        )
        await self._confirm_update_post_components(interaction, confirm)

################################################################################
    async def set_order(self, interaction: Interaction) -> None:

        options = []
        for tier in self._mgr.tiers:
            if tier == self:
                continue
            option = tier.select_option()
            option.description = f" (Position {tier.order})"
            options.append(option)

        prompt = U.make_embed(
            title="Set Display Order",
            description=(
                "Select the position you would like to move this tier to.\n\n"

                "Tiers will be appropriately shifted to fill the gap left by "
                "the moved tier."
            )
        )
        view = FroggeSelectView(interaction.user, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        new_order = self._mgr[view.value].order

        if self.order < new_order:
            for tier in self._mgr.tiers:
                if self.order < tier.order <= new_order:
                    tier.order -= 1
        else:
            for tier in self._mgr.tiers:
                if new_order <= tier.order < self.order:
                    tier.order += 1

        self.order = new_order

        confirm = U.make_embed(
            title="Display Order Updated",
            description=(
                f"Tier `{self.name}` has been moved to position `{new_order}`.\n\n"

                "Would you like to update any existing VIP List messages to "
                "reflect the new change?"
            )
        )
        await self._confirm_update_post_components(interaction, confirm)

################################################################################
    async def _confirm_update_post_components(self, interaction: Interaction, confirm: Embed) -> None:

        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        await self.guild.vip_manager.update_post_components()

################################################################################
    async def set_thumbnail(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="Set Thumbnail",
            description=(
                "Enter the image you would like to use as the thumbnail for this tier."
            )
        )
        if thumbnail := await U.wait_for_image(interaction, prompt):
            self.thumbnail = thumbnail

        confirm = U.make_embed(
            title="Thumbnail Updated",
            description=(
                f"The thumbnail for this VIP Tier has been replaced.\n\n"

                "Would you like to update any existing VIP List messages to "
                "reflect the new change?"
            )
        )
        await self._confirm_update_post_components(interaction, confirm)

################################################################################
