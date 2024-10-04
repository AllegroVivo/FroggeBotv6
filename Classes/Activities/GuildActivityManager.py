from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from discord import Embed, Interaction

from Classes.Giveaways.GiveawayManager import GiveawayManager
from Classes.Raffles.RaffleManager import RaffleManager
from UI.Core import ActivitiesMainMenuView
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import GuildData
################################################################################

__all__ = ("GuildActivityManager",)

################################################################################
class GuildActivityManager:

    __slots__ = (
        "_state",
        "_giveaway_mgr",
        "_raffle_mgr",
        "_tournament_mgr",
        "_contest_mgr",
    )

################################################################################
    def __init__(self, state: GuildData) -> None:

        self._state: GuildData = state

        self._giveaway_mgr: GiveawayManager = GiveawayManager(self._state)
        self._raffle_mgr: RaffleManager = RaffleManager(self._state)
        # self._tournament_mgr: TournamentManager = TournamentManager(self._state)
        # self._contest_mgr: ContestManager = ContestManager(self._state)

################################################################################
    async def load_all(self, payload: Dict[str, Any]) -> None:

        await self._giveaway_mgr.load_all(payload["giveaways"])
        await self._raffle_mgr.load_all(payload["raffles"])
        # await self._tournament_mgr.load_all(data["tournaments"])
        # await self._contest_mgr.load_all(data["contests"])

################################################################################
    @property
    def giveaway_manager(self) -> GiveawayManager:

        return self._giveaway_mgr

################################################################################
    @property
    def raffle_manager(self) -> RaffleManager:

        return self._raffle_mgr

################################################################################
    @property
    def tournament_manager(self) -> TournamentManager:

        return self._tournament_mgr

################################################################################
    @property
    def contest_manager(self) -> ContestManager:

        return self._contest_mgr

################################################################################
    def status(self) -> Embed:

        return U.make_embed(
            title="__Activities Module__",
            description=(
                "Manage the current activities in this server with the "
                "buttons below.\n\n"

                f"**[`{len(self.giveaway_manager)}`]** active giveaways\n"
                f"**[`{len(self.raffle_manager)}`]** active raffles\n"
                # f"**[`{len(self.tournament_manager)}`]** active tournaments\n"
                # f"**[`{len(self.contest_manager)}`]** active contests"
            ),
        )

################################################################################
    async def main_menu(self, interaction: Interaction) -> None:

        embed = self.status()
        view = ActivitiesMainMenuView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
