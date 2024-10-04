from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from discord import Interaction, User, Embed, EmbedField, Message

from Classes.Activities import ActivityManager
from Classes.Common import LazyChannel
from Utilities import Utilities as U
from .Giveaway import Giveaway
from UI.Giveaways import GiveawayManagerMenuView

if TYPE_CHECKING:
    from Classes import GuildData
    from UI.Common import FroggeView
################################################################################

__all__ = ("GiveawayManager", )

################################################################################
class GiveawayManager(ActivityManager):

    def __init__(self, state: GuildData) -> None:

        super().__init__(state, Giveaway)
    
################################################################################
    async def load_all(self, payload: Dict[str, Any]) -> None:

        self._managed = [Giveaway.load(self, g) for g in payload["giveaways"]]
        self._channel = LazyChannel(self, payload["channel_id"])

################################################################################
    async def status(self) -> Embed:

        channel = await self.channel
        return U.make_embed(
            title="__Giveaway Module Status__",
            description=(
                f"Current Active Giveaways: **[`{len(self.active_items)}`]**"
            ),
            fields=[
                EmbedField(
                    name="__Giveaways Channel__",
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

        return GiveawayManagerMenuView(user, self)

################################################################################
    async def roll_giveaway_ctx(self, interaction: Interaction, msg: Message) -> None:

        try:
            # Get the giveaway ID from the message footer
            # 'Giveaway ID: 1234567890'
            giveaway_id = msg.embeds[0].footer.text.split(":")[1].strip()
        except:
            error = U.make_error(
                title="Invalid Giveaway",
                message="The message you've selected as a giveaway is invalid.",
                solution="Please make sure the message you've selected is a valid giveaway system message."
            )
            await interaction.respond(embed=error)
        else:
            await self[giveaway_id].determine_winners(interaction)  # type: ignore

################################################################################
