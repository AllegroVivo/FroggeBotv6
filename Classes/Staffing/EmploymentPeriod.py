from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, Any

from discord import SelectOption, Interaction, Embed, EmbedField

from Classes.Common import Identifiable
from UI.Common import DateTimeModal, ConfirmCancelView
from UI.Staffing import EmploymentPeriodStatusView
from Utilities import Utilities as U
from Enums import Timezone

if TYPE_CHECKING:
    from Classes import StaffDetails, FroggeBot
################################################################################

__all__ = ("EmploymentPeriod", )

################################################################################
class EmploymentPeriod(Identifiable):

    __slots__ = (
        "_parent",
        "_hire_date",
        "_termination_date",
    )

################################################################################
    def __init__(
        self,
        parent: StaffDetails,
        _id: int,
        hire: datetime,
        term: Optional[datetime] = None
    ) -> None:

        super().__init__(_id)

        self._parent: StaffDetails = parent

        self._hire_date: datetime = hire
        self._termination_date: Optional[datetime] = term

################################################################################
    @classmethod
    def new(cls, parent: StaffDetails) -> EmploymentPeriod:

        new_data = parent.bot.api.create_employment_date(parent._parent.id)
        return cls(parent, new_data["id"], datetime.fromisoformat(new_data["hire_date"]))

################################################################################
    @classmethod
    def load(cls, parent: StaffDetails, data: Dict[str, Any]) -> EmploymentPeriod:

        return cls(
            parent,
            data["id"],
            datetime.fromisoformat(data["hire_date"]),
            datetime.fromisoformat(data["termination_date"]) if data["termination_date"] else None
        )

################################################################################
    @property
    def bot(self) -> FroggeBot:

        return self._parent.bot

################################################################################
    @property
    def id(self) -> int:

        return self._id

################################################################################
    @property
    def hire_date(self) -> datetime:

        return self._hire_date

    @hire_date.setter
    def hire_date(self, value: datetime) -> None:

        self._hire_date = value
        self.update()

################################################################################
    @property
    def termination_date(self) -> Optional[datetime]:

        return self._termination_date

    @termination_date.setter
    def termination_date(self, value: datetime) -> None:

        self._termination_date = value
        self.update()

################################################################################
    @property
    def tz(self) -> Timezone:

        return self._parent._parent.timezone

    @property
    def py_tz(self):

        return self._parent._parent.py_tz

################################################################################
    def select_option(self) -> SelectOption:

        return SelectOption(
            label=f"{self._hire_date.strftime('%Y-%m-%d')}",
            value=str(self._id)
        )

################################################################################
    def update(self) -> None:

        self.bot.api.update_employment_date(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "hire_date": self.hire_date.isoformat(),
            "termination_date": self.termination_date.isoformat() if self.termination_date else None
        }

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_employment_date(self.id)

################################################################################
    def status(self) -> Embed:

        return U.make_embed(
            title="__Employee Employment Period__",
            fields=[
                EmbedField(
                    name="Hire Date",
                    value=U.format_dt(self.hire_date, 'd'),
                    inline=True
                ),
                EmbedField(
                    name="Termination Date",
                    value=(
                        U.format_dt(self.termination_date, 'd')
                        if self.termination_date
                        else "`---- N/A ----`"
                    ),
                    inline=True
                )
            ]
        )

################################################################################
    async def menu(self, interaction: Interaction) -> None:

        embed = self.status()
        view = EmploymentPeriodStatusView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def set_hire_date(self, interaction: Interaction) -> None:

        modal = DateTimeModal("Hire Date", U.ensure_timezone(self.hire_date, self.tz))

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.hire_date = self.py_tz.localize(modal.value)

################################################################################
    async def set_termination_date(self, interaction: Interaction) -> None:

        dt = U.ensure_timezone(self.termination_date, self.tz) if self.termination_date else None
        modal = DateTimeModal("Termination Date", dt)

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.termination_date = self.py_tz.localize(modal.value)

################################################################################
    def terminate(self) -> None:

        self.termination_date = self.py_tz.localize(datetime.now())

################################################################################
    async def remove(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Employment Period__",
            description="Are you sure you want to remove this employment period?"
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.delete()

################################################################################
