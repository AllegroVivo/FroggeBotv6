from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from discord import User, Embed, EmbedField, Interaction

from Classes.Activities import ActivityManager
from .Raffle import Raffle
from Classes.Common import LazyChannel
from Utilities import Utilities as U
from UI.Raffles import RaffleManagerMenuView

if TYPE_CHECKING:
    from Classes import GuildData
    from UI.Common import FroggeView
################################################################################

__all__ = ("RaffleManager", )

################################################################################
class RaffleManager(ActivityManager):

    def __init__(self, parent: GuildData) -> None:

        super().__init__(parent, Raffle)

################################################################################
    async def load_all(self, payload: Dict[str, Any]) -> None:

        self._managed = [Raffle.load(self, r) for r in payload["raffles"]]
        self._channel = LazyChannel(self, payload["channel_id"])

################################################################################
    @property
    def active_raffle(self) -> Optional[Raffle]:

        for raffle in self.active_items:
            if raffle._active:  # type: ignore
                return raffle  # type: ignore

################################################################################
    def update(self) -> None:

        self.bot.api.update_raffle_manager(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "channel_id": self._channel.id
        }

################################################################################
    async def status(self) -> Embed:

        channel = await self.channel
        return U.make_embed(
            title="__Raffle Module Status__",
            description=(
                f"Current Active Raffles: **[`{len(self.active_items)}`]**"
            ),
            fields=[
                EmbedField(
                    name="__Raffle Post Channel__",
                    value=(
                        channel.mention
                        if channel is not None
                        else "`Not Set`"
                    ),
                    inline=False
                )
            ]
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return RaffleManagerMenuView(user, self)

################################################################################
    async def add_tickets(self, interaction: Interaction, user: User, qty: int) -> None:

        if self.active_raffle is None:
            error = U.make_error(
                title="No Active Raffle",
                message="No active raffle is currently marked as 'active'.",
                solution="Please create a new raffle or activate an existing one."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        await self.active_raffle.add_tickets(interaction, user, qty)

################################################################################
