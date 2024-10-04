from __future__ import annotations

from typing import TYPE_CHECKING, Type, Tuple, Any, TypeVar, Dict

from discord import User, Forbidden, NotFound, Interaction

from Classes.Activities import ActivityEntry
from Utilities.Constants import *
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import Raffle, BaseActivity
################################################################################

__all__ = ("RaffleEntry", )

RE = TypeVar("RE", bound="RaffleEntry")

################################################################################
class RaffleEntry(ActivityEntry):

    def __init__(self, parent: Raffle, _id: int, user_id: int, qty: int) -> None:

        super().__init__(parent, _id, user_id, qty)

################################################################################
    @classmethod
    def new(cls: Type[RE], parent: Raffle, user_id: int, qty: int = 1) -> RE:

        new_data = parent.bot.api.create_raffle_entry(parent.id, user_id, qty)
        return cls(parent, new_data["id"], user_id, qty)

################################################################################
    @classmethod
    def load(cls: Type[RE], parent: Raffle, data: Dict[str, Any]) -> RE:

        return cls(
            parent=parent,
            _id=data["id"],
            user_id=data["user_id"],
            qty=data["quantity"]
        )

################################################################################
    def update(self) -> None:

        self.bot.api.update_raffle_entry(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "quantity": self.quantity
        }

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_raffle_entry(self.id)

################################################################################
    async def notify(self) -> bool:

        embed = U.make_embed(
            title=f"__YOU WON!__",
            description=(
                f"Congratulations! You have won the raffle for **{self._parent.prize}**! "
                f"in the **{self._parent.name}** raffle!\n\n"

                f"Please contact the host or a manager to claim your prize!"
            ),
        )

        user = await self.user
        try:
            await user.send(embed=embed)
        except NotFound:
            await self._parent.guild.log.user_not_found(user)
            return False
        except Forbidden:
            await self._parent.guild.log.dms_closed(user)
            return False
        else:
            await self._parent.guild.log.raffle_winner_notified(self)
            return True

################################################################################
    async def add_tickets(self, interaction: Interaction, qty: int) -> None:

        if self.quantity >= MAX_RAFFLE_ENTRIES:
            error = U.make_error(
                title="Max Raffle Entries Reached",
                description=f"**Maximum Raffle Entries:** `{MAX_RAFFLE_ENTRIES}`",
                message="This user has reached the maximum number of entries for this raffle.",
                solution="Please wait until the raffle is drawn to enter again."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        self.quantity += qty

################################################################################
