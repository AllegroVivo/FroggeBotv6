from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Interaction, PartialEmoji, ButtonStyle
from discord.ui import View

from Assets import BotEmojis
from UI.Common import FroggeButton

if TYPE_CHECKING:
    from Classes import Giveaway
################################################################################

__all__ = ("GiveawaySignupView",)

################################################################################
class GiveawaySignupView(View):

    def __init__(self, giveaway: Giveaway):
        
        super().__init__(timeout=None)
        
        self.giveaway: Giveaway = giveaway

        self.add_item(GiveawaySignupButton(giveaway))
        
################################################################################
class GiveawaySignupButton(FroggeButton):
    
    def __init__(self, giveaway: Giveaway):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Enter Giveaway",
            disabled=False,
            row=0,
            emoji=giveaway.emoji or BotEmojis.PartyPopper,
            custom_id=f"giveaway_signup-{giveaway.id}"
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.giveaway.signup(interaction)
        await self.view.giveaway.update_post_components()
        
################################################################################
