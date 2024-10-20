from __future__ import annotations

from typing import TYPE_CHECKING, Type, Tuple, Any, TypeVar, Dict

from discord import User, NotFound, Forbidden

from Classes.Activities import ActivityEntry
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import Giveaway
################################################################################

__all__ = ("GiveawayEntry", )

GE = TypeVar("GE", bound="GiveawayEntry")

################################################################################
class GiveawayEntry(ActivityEntry):

    def __init__(self, parent: Giveaway, _id: int, user_id: int) -> None:

        super().__init__(parent, _id, user_id, 1)

################################################################################
    @classmethod
    def new(cls: Type[GE], parent: Giveaway, user: User) -> GE:

        new_data = parent.bot.api.create_giveaway_entry(parent.id, user.id)
        return cls(parent=parent, _id=new_data["id"], user_id=user.id)

################################################################################
    @classmethod
    def load(cls: Type[GE], parent: Giveaway, data: Dict[str, Any]) -> GE:

        return cls(
            parent=parent,
            _id=data["id"],
            user_id=data["user_id"]
        )

################################################################################
    def update(self) -> None:

        pass

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_giveaway_entry(self.id)
        self._parent.entries.remove(self)

################################################################################
    async def notify(self) -> bool:

        embed = U.make_embed(
            title=f"__YOU WON!__",
            description=(
                f"You have won the giveaway `{self._parent.name}` for the prize of "
                f"**`{self._parent.prize}`**!\n\n"

                f"Please contact management or a host to claim your prize!"
            ),
        )

        user = await self.user
        try:
            await user.send(embed=embed)
        except NotFound:
            await self._parent.guild.log.user_not_found(user)
            return False
        except Forbidden:
            await self._parent.guild.log.dms_closed(await self.user)
            return False
        else:
            await self._parent.guild.log.giveaway_winner_notified(self)
            return True

################################################################################
