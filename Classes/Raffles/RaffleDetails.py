from __future__ import annotations

from typing import TYPE_CHECKING, Type, Any, TypeVar, Dict

from discord import Interaction

from Classes.Activities import ActivityDetails
from UI.Common import BasicNumberModal, InstructionsInfo

if TYPE_CHECKING:
    from Classes import Raffle
################################################################################

__all__ = ("RaffleDetails", )

RD = TypeVar("RD", bound="RaffleDetails")

################################################################################
class RaffleDetails(ActivityDetails):

    __slots__ = (
        "_cost",
    )

################################################################################
    def __init__(self, parent: Raffle, **kwargs) -> None:

        prize = kwargs.pop("prize", "50/50")

        super().__init__(parent, prize=prize, **kwargs)

        self._cost: int = kwargs.get("cost", 100000)

################################################################################
    @classmethod
    def load(cls: Type[RD], parent: Raffle, data: Dict[str, Any]) -> RD:

        return cls(
            parent=parent,
            name=data["name"],
            num_winners=data["num_winners"],
            auto_notify=data["auto_notify"],
            cost=data["cost"],
            prize=data["prize"],
        )

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
    def winner_pct(self) -> int:

        return int(self.prize.split("/")[0])

    @winner_pct.setter
    def winner_pct(self, value: int) -> None:

        assert 0 <= value <= 100, "Winner percentage must be between 0 and 100"

        self.prize = f"{value}/{100 - value}"
        self.update()

################################################################################
    @property
    def venue_pct(self) -> int:

        return int(self.prize.split("/")[1])

################################################################################
    def update(self) -> None:

        self.bot.api.update_raffle_details(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "name": self.name,
            "num_winners": self.num_winners,
            "auto_notify": self.auto_notify,
            "cost": self.cost,
            "prize": self.prize,
        }

################################################################################
    async def set_prize(self, interaction: Interaction) -> None:

        modal = BasicNumberModal(
            title="Set Raffle Winner Percent",
            attribute="Winner Pct.",
            cur_val=self.winner_pct,
            example="eg. '80'",
            max_length=3,
            instructions=InstructionsInfo(
                placeholder="Enter the winner's percentage payout.",
                value=(
                    "Enter the percentage of the total prize pool that the winner "
                    "will receive. The remaining percentage will be given to the "
                    "venue."
                )
            )
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.winner_pct = modal.value

################################################################################
    async def set_cost(self, interaction: Interaction) -> None:

        modal = BasicNumberModal(
            title="Set Raffle Ticket Cost",
            attribute="Ticket Cost",
            cur_val=self.cost,
            example="eg. '100000' or '100k' or '1.2m'",
            max_length=11
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.cost = modal.value

################################################################################

