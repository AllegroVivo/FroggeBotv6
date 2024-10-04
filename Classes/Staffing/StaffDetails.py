from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional, Type, TypeVar, List, Any, Dict

from discord import Interaction, Embed, EmbedField

from Errors import MaxItemsReached
from .EmploymentPeriod import EmploymentPeriod
from UI.Common import BasicTextModal, InstructionsInfo, FroggeSelectView
from UI.Staffing import EmploymentHistoryMenuView
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import StaffMember, FroggeBot
################################################################################

__all__ = ("StaffDetails", )

SD = TypeVar("SD", bound="StaffDetails")

################################################################################
class StaffDetails:

    __slots__ = (
        "_parent",
        "_name",
        "_birthday",
        "_notes",
        "_employment_dates",
    )

    MAX_EMPLOYMENT_DATES = 10

################################################################################
    def __init__(self, parent: StaffMember, **kwargs) -> None:

        self._parent: StaffMember = parent

        self._name: Optional[str] = kwargs.get("name")
        self._birthday: Optional[date] = kwargs.get("birthday")
        self._notes: Optional[str] = kwargs.get("notes")

        self._employment_dates: List[EmploymentPeriod] = (
            kwargs.get("employment_dates", None) or [EmploymentPeriod.new(self)]
        )

################################################################################
    @classmethod
    def load(cls: Type[SD], parent: StaffMember, data: Dict[str, Any], dates: List[Dict[str, Any]]) -> SD:

        self: SD = cls.__new__(cls)

        self._parent = parent
        self._name = data["name"]
        self._birthday = date.fromisoformat(data["birthday"]) if data["birthday"] else None
        self._notes = data["notes"]

        self._employment_dates = [EmploymentPeriod.load(self, ep) for ep in dates]

        return self

################################################################################
    @property
    def bot(self) -> FroggeBot:

        return self._parent.bot

################################################################################
    @property
    def employment_dates(self) -> List[EmploymentPeriod]:

        return self._employment_dates

################################################################################
    @property
    def name(self) -> Optional[str]:

        return self._name

    @name.setter
    def name(self, value: str) -> None:

        self._name = value
        self.update()

################################################################################
    @property
    def birthday(self) -> Optional[date]:

        return self._birthday

    @birthday.setter
    def birthday(self, value: Optional[date]) -> None:

        self._birthday = value
        self.update()

################################################################################
    @property
    def notes(self) -> Optional[str]:

        return self._notes

    @notes.setter
    def notes(self, value: Optional[str]) -> None:

        self._notes = value
        self.update()

################################################################################
    @property
    def is_terminated(self) -> bool:

        return all(ep.termination_date is not None for ep in self.employment_dates)

################################################################################
    def update(self) -> None:

        self.bot.api.update_staff_details(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "name": self.name,
            "birthday": self.birthday.isoformat() if self.birthday else None,
            "notes": self.notes,
        }

################################################################################
    async def set_name(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Enter Staff Member Name",
            attribute="Staff Member Name",
            cur_val=self.name,
            example="e.g. 'Allegro Vivo'",
            max_length=40,
            required=False,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.name = modal.value

################################################################################
    async def set_birthday(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Enter Staff Member Birthday",
            attribute="Birthday",
            cur_val=self.birthday.strftime("%m/%d") if self.birthday else None,
            example="e.g. '02/06'",
            max_length=5,
            required=False,
            instructions=InstructionsInfo(
                placeholder="Enter the staff member's birthday without year.",
                value=(
                    "Enter the staff member's birthday, without year, in the "
                    "format MM/DD. This information is optional."
                )
            )
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        raw_birthday = modal.value

        try:
            birthday = datetime.strptime(raw_birthday, "%m/%d")
            birthday_with_year = birthday.replace(year=datetime.now().year)
            self.birthday = birthday_with_year.date()
        except ValueError:
            error = U.make_error(
                title="Invalid Date Entered",
                description=f"**Invalid Date Value:** `{modal.value}`",
                message="The date you entered is not in a valid format.",
                solution=f"Please enter a date in the format `MM/DD`."
            )
            await interaction.respond(embed=error, ephemeral=True)

################################################################################
    async def set_notes(self, interaction: Interaction):

        modal = BasicTextModal(
            title="Enter Employee Notes",
            attribute="Notes",
            cur_val=self.notes,
            max_length=1000,
            multiline=True
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.notes = modal.value

################################################################################
    def get_employment_period(self, period_id: str) -> Optional[EmploymentPeriod]:

        return next((ep for ep in self.employment_dates if ep.id == period_id), None)

################################################################################
    def get_current_employment_period(self) -> Optional[EmploymentPeriod]:

        return next((ep for ep in self.employment_dates if ep.termination_date is None), None)

################################################################################
    def employment_history_status(self) -> Embed:

        return U.make_embed(
            title="__Employment History Status__",
            fields=[
                EmbedField(
                    name="Current Hire Date",
                    value=(
                        U.format_dt(self.get_current_employment_period().hire_date, 'd')
                        if self.get_current_employment_period()
                        else "`----- N/A -----`"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="Previous Employment Periods",
                    value=(
                        "\n".join(
                            f"{U.format_dt(ep.hire_date, 'd')} - "
                            f"{U.format_dt(ep.termination_date, 'd')}"
                            for ep in self.employment_dates if ep.termination_date
                        )
                        if self.employment_dates
                        else "`---------- N/A ----------`"
                    ),
                )
            ]
        )

################################################################################
    async def employment_history_menu(self, interaction: Interaction) -> None:

        embed = self.employment_history_status()
        view = EmploymentHistoryMenuView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def add_employment_date(self, interaction: Interaction) -> None:

        if len(self.employment_dates) >= self.MAX_EMPLOYMENT_DATES:
            error = MaxItemsReached("Employment Periods", self.MAX_EMPLOYMENT_DATES)
            await interaction.respond(embed=error, ephemeral=True)
            return

        ep = EmploymentPeriod.new(self)
        self.employment_dates.append(ep)

        await ep.set_hire_date(interaction)

################################################################################
    async def modify_employment_date(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Modify Employment Period__",
            description=(
                "Please select the employment period you would like to modify."
            )
        )
        view = FroggeSelectView(interaction.user, [ep.select_option() for ep in self.employment_dates])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        ep = self.get_employment_period(view.value)
        await ep.menu(interaction)

################################################################################
    async def remove_employment_date(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Employment Period__",
            description=(
                "Please select the employment period you would like to remove."
            )
        )
        view = FroggeSelectView(interaction.user, [ep.select_option() for ep in self.employment_dates])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        ep = self.get_employment_period(view.value)
        await ep.remove(interaction)

################################################################################

