from __future__ import annotations

import random
from abc import ABC
from typing import TYPE_CHECKING, List, Optional

from discord import Interaction, SelectOption
from discord.ext.pages import Page

from Classes.Common import ManagedObject
from Errors import NoEntries
from UI.Common import ConfirmCancelView
from Utilities import Utilities as U
from .ActivityDetails import ActivityDetails
from .ActivityEntry import ActivityEntry

if TYPE_CHECKING:
    from Classes import ActivityManager, StaffableEvent
################################################################################

__all__ = ("BaseActivity", )

################################################################################
class BaseActivity(ManagedObject, ABC):

    __slots__ = (
        "_details",
        "_entries",
        "_winners",
        "_event",
    )
    
################################################################################
    def __init__(
        self,
        mgr: ActivityManager, 
        _id: int,
        details: ActivityDetails,
        entries: List[ActivityEntry],
        winners: List[ActivityEntry],
    ) -> None:

        super().__init__(mgr, _id)
        
        self._details: ActivityDetails = details
        self._entries: List[ActivityEntry] = entries
        self._winners: List[ActivityEntry] = winners
    
################################################################################
    def __getitem__(self, user_id: int) -> Optional[ActivityEntry]:

        for entry in self.entries:
            if entry.user.id == user_id:
                return entry

################################################################################
    @property
    def name(self) -> str:
        
        return self._details.name
    
################################################################################
    @property
    def prize(self) -> str:
        
        return self._details.prize
    
################################################################################
    @property
    def num_winners(self) -> int:
        
        return self._details.num_winners
    
################################################################################
    @property
    def auto_notify(self) -> bool:
        
        return self._details.auto_notify
    
################################################################################
    @property
    def entries(self) -> List[ActivityEntry]:
        
        return self._entries
    
################################################################################
    @property
    def winners(self) -> List[ActivityEntry]:
        
        return self._winners
    
    @winners.setter
    def winners(self, value: List[ActivityEntry]) -> None:
        
        self._winners = value
        self.update()
        
################################################################################
    def is_active(self) -> bool:
        
        return len(self._winners) == 0
    
################################################################################
    @property
    def activity_name(self) -> str:

        match self.__class__.__name__:
            case "GPoseContest":
                return "GPose Contest"
            case "GlamourContest":
                return "Glamour Contest"
            case "DeathrollTournament":
                return "Deathroll Tournament"
            case _:
                return self.__class__.__name__

################################################################################
    async def set_name(self, interaction: Interaction) -> None:
        
        await self._details.set_name(interaction)
        
################################################################################
    async def set_prize(self, interaction: Interaction) -> None:
        
        await self._details.set_prize(interaction)
        
################################################################################
    async def set_num_winners(self, interaction: Interaction) -> None:
        
        await self._details.set_num_winners(interaction)
        
################################################################################
    async def toggle_auto_notify(self, interaction: Interaction) -> None:
        
        await self._details.toggle_auto_notify(interaction)
        
################################################################################
    async def determine_winners(self, interaction) -> None:

        if not self._entries:
            error = NoEntries(self.activity_name)
            await interaction.respond(embed=error, ephemeral=True)
            return

        if self.winners:
            confirm = U.make_embed(
                title="__Winner(s) Already Determined__",
                description=(
                    f"You've already determined a winner(s) for this raffle!\n\n"
        
                    "Are you sure you want to re-select the winner(s)? If auto-notify "
                    "is enabled, the new winner(s) will be notified immediately."
                )
            )
            view = ConfirmCancelView(interaction.user)
        
            await interaction.respond(embed=confirm, view=view)
            await view.wait()
        
            if not view.complete or view.value is False:
                return
        
        self.winners = random.sample(self._entries, self.num_winners)
        
        if self._details.auto_notify:
            for winner in self.winners:
                await winner.notify()
    
################################################################################
    def select_option(self) -> SelectOption:
        
        return SelectOption(
            label=self.name or f"Unnamed {self.activity_name}",
            value=str(self.id)
        )
    
################################################################################
    async def remove(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title=f"__Remove {self.activity_name.title()}__",
            description=(
                f"Are you sure you want to remove this {self.activity_name.lower()}?\n"
                "This action cannot be undone."
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.delete()

        confirm = U.make_embed(
            title=f"__{self.activity_name.title()} Removed__",
            description=f"The {self.activity_name.lower()} has been successfully removed."
        )
        await interaction.respond(embed=confirm)
    
################################################################################
    async def page(self) -> Page:
        
        raise NotImplementedError
    
################################################################################
    async def generate_entries_report_str(self, final: bool = False) -> str:

        entry_data = (
            f"{self.activity_name} Entry Data for {self.name}:\n\n"
        )
        # self.entries.sort(key=lambda x: x.user.display_name)
        for entry in self.entries:
            user = await entry.user
            if final and entry in self.winners:
                entry_data += "**"
            entry_data += (
                f"{user.display_name} - {entry.quantity}x entries - ({user.id})"
            )
            if final and entry in self.winners:
                entry_data += " - WINNER\n"
            else:
                entry_data += "\n"
            
        return entry_data
    
################################################################################
    