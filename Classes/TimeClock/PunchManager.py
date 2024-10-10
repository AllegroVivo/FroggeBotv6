from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

from discord import Interaction, User, Embed

from Classes.Common import ObjectManager
from Utilities.Constants import DEFAULT_CLOCK_THRESHOLD_MINUTES
from .Punch import Punch
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import GuildData, EventManager, StaffMember, Event
    from UI.Common import FroggeView
################################################################################

__all__ = ("PunchManager", )

################################################################################
class PunchManager(ObjectManager):

    __slots__ = (
        "_threshold",
    )

################################################################################
    def __init__(self, state: GuildData) -> None:

        super().__init__(state)

        self._threshold: int = DEFAULT_CLOCK_THRESHOLD_MINUTES

################################################################################
    async def load_all(self, payload: Any) -> None:

        pass

################################################################################
    @property
    def event_manager(self) -> EventManager:

        return self._state.event_manager

################################################################################
    @property
    def punches(self) -> List[Punch]:

        self._managed.sort(key=lambda x: x.in_time)
        return self._managed  # type: ignore

################################################################################
    async def status(self) -> Embed:

        pass

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        pass

################################################################################
    async def add_item(self, interaction: Interaction) -> None:

        pass

################################################################################
    async def modify_item(self, interaction: Interaction) -> None:

        pass

################################################################################
    async def remove_item(self, interaction: Interaction) -> None:

        pass

################################################################################
    def get_open_punch(self, staff: StaffMember) -> Optional[Punch]:

        return next(
            (p for p in self.punches if p.staff == staff and p.out_time is None),
            None
        )

################################################################################
    async def process_punch_in(self, interaction: Interaction, event: Optional[Event] = None) -> None:

        staff = self.guild.staff_manager[interaction.user.id]
        if staff is None:
            error = U.make_error(
                title="Staff Member Not Found",
                message="You are not a registered staff member and therefore may not clock in.",
                solution="Please contact a manager to be added to the staff roster."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        current = self.get_open_punch(staff)
        if current is not None:
            error = U.make_error(
                title="Already Clocked In",
                message="You are already clocked in to a shift.",
                solution="If you need to clock out, please use the appropriate command."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        if not staff.qualifications.positions:
            error = U.make_error(
                title="No Qualifications",
                message="You do not have any qualifications to work any positions.",
                solution="Please contact a manager to be assigned to a position."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        assert len(staff.qualifications.positions) > 0, "Staff member has no qualifications."

        if event is None:
            new_punch = Punch.new(

            )

        position = staff.qualifications.positions[0]
        if len(staff.qualifications.positions) > 1:
            prompt = U.make_embed(
                title="__Select Position__",
                description="You have multiple qualifications. Please select the position you are working.",
            )

################################################################################
