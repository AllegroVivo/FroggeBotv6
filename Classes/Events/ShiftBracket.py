from __future__ import annotations

from datetime import datetime, timedelta, date, UTC
from typing import TYPE_CHECKING, Type, TypeVar, Optional, Any, Dict, List

from discord import Interaction, Embed, EmbedField, SelectOption

from Classes.Common import Identifiable
from Enums import Timezone, Hours, Minutes
from UI.Common import TimeSelectView, ConfirmCancelView
from UI.Events import ShiftBracketStatusView
from Utilities import Utilities as U
from logger import log

if TYPE_CHECKING:
    from Classes import Event, FroggeBot, GuildData, StaffMember
################################################################################

__all__ = ("ShiftBracket", )

SB = TypeVar("SB", bound="ShiftBracket")

################################################################################
class ShiftBracket(Identifiable):

    __slots__ = (
        "_parent",
        "_start",
        "_end",
    )

################################################################################
    def __init__(self, parent: Event, _id: int, start_time: datetime, end_time: datetime) -> None:

        super().__init__(_id)

        self._parent: Event = parent

        self._start: datetime = start_time
        self._end: datetime = end_time

################################################################################
    @classmethod
    def new(cls: Type[SB], parent: Event, start_time: datetime, end_time: datetime) -> SB:

        data = parent.bot.api.create_shift_bracket(parent.id, start_time, end_time)
        return cls(parent, data["id"], start_time, end_time)

################################################################################
    @classmethod
    def load(cls: Type[SB], parent: Event, data: Dict[str, Any]) -> SB:

        return cls(
            parent=parent,
            _id=data["id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"])
        )

################################################################################
    @classmethod
    def copy(cls: Type[SB], parent: Event, other: ShiftBracket) -> SB:

        if other.start_time and other.end_time:
            year = datetime.now(UTC).year
            start_day = end_day = datetime.now(UTC).day
            if other.end_time.time() < other.start_time.time():
                end_day += 1

            start_time = other.start_time.replace(day=start_day, year=year)
            end_time = other.end_time.replace(day=end_day, year=year)
        else:
            start_time = end_time = None

        return cls.new(parent, start_time, end_time)

################################################################################
    @property
    def bot(self) -> FroggeBot:

        return self._parent.bot

################################################################################
    @property
    def guild(self) -> GuildData:

        return self._parent.guild

################################################################################
    @property
    def start_time(self) -> datetime:

        return self._start

    @start_time.setter
    def start_time(self, value: datetime) -> None:

        self._start = value
        self.update()

################################################################################
    @property
    def end_time(self) -> datetime:

        return self._end

    @end_time.setter
    def end_time(self, value: datetime) -> None:

        self._end = value
        self.update()

################################################################################
    @property
    def staff(self) -> List[StaffMember]:

        ret = []

        for pos in self._parent.positions:
            for signup in pos.signups:
                if signup.bracket == self:
                    ret.append(signup.staff_member)

        return ret

################################################################################
    @property
    def length(self) -> int:

        start_time_with_tz = self.start_time
        end_time_with_tz = self.end_time

        # Adjust end time if it is on the next day
        if end_time_with_tz < start_time_with_tz:
            end_time_with_tz += timedelta(days=1)

        ret = int((end_time_with_tz - start_time_with_tz).total_seconds() // 60)
        return ret

################################################################################
    def select_option(self) -> SelectOption:

        local_start = self.start_time.astimezone(self._parent.py_tz)
        local_end = self.end_time.astimezone(self._parent.py_tz)

        return SelectOption(
            label=(
                f"{local_start.strftime('%I:%M %p')} - "
                f"{local_end.strftime('%I:%M %p')}"
            ),
            value=str(self.id)
        )

################################################################################
    def update(self) -> None:

        self.bot.api.update_shift_bracket(self)

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_shift_bracket(self.id)
        try:
            self._parent._shifts.remove(self)
        except ValueError:
            pass

################################################################################
    def overlaps_with(self, other: ShiftBracket) -> bool:

        # Normalize the times to a duration from the start of the respective days
        def normalize_time(dt: datetime) -> timedelta:
            return timedelta(hours=dt.hour, minutes=dt.minute)

        self_start_duration = normalize_time(self.start_time)
        self_end_duration = normalize_time(self.end_time)
        other_start_duration = normalize_time(other.start_time)
        other_end_duration = normalize_time(other.end_time)

        # Handle shifts that end after midnight
        if self_end_duration < self_start_duration:
            self_end_duration += timedelta(days=1)
        if other_end_duration < other_start_duration:
            other_end_duration += timedelta(days=1)

        # Normalize the start and end durations to the same day
        self_start = self.start_time.replace(hour=0, minute=0, second=0, microsecond=0) + self_start_duration
        self_end = self.start_time.replace(hour=0, minute=0, second=0, microsecond=0) + self_end_duration
        other_start = other.start_time.replace(hour=0, minute=0, second=0, microsecond=0) + other_start_duration
        other_end = other.start_time.replace(hour=0, minute=0, second=0, microsecond=0) + other_end_duration

        return self_start < other_end and self_end > other_start

################################################################################
    def status(self) -> Embed:

        return U.make_embed(
            title="__Shift Bracket Status__",
            description=(
                "__Event Schedule:__\n"
                f"**Date:** {U.format_dt(self._parent.start_time, 'd')}\n"
                f"**Start Time:** {U.format_dt(self._parent.start_time, 't')}\n"
                f"**End Time:** {U.format_dt(self._parent.end_time, 't')}"
            ),
            fields=[
                EmbedField(
                    name="Shift Start Time",
                    value=U.format_dt(self.start_time, "f"),
                    inline=True
                ),
                EmbedField(
                    name="Shift End Time",
                    value=U.format_dt(self.end_time, "f"),
                    inline=True
                ),
            ]
        )

################################################################################
    async def menu(self, interaction: Interaction) -> None:

        log.info(self.guild, f"ShiftBracket.menu({self.id})")

        embed = self.status()
        view = ShiftBracketStatusView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    @staticmethod
    async def get_single_time(
        interaction: Interaction,
        prompt: Optional[Embed],
        _date: Optional[date] = None,
        tz: Timezone = Timezone.UTC
    ) -> Optional[datetime]:

        prompt = prompt or U.make_embed(
            title="__Set Time__",
            description="Please select a time..."
        )
        view = TimeSelectView(interaction.user, Hours.select_options(), Minutes.select_options())

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        _date = _date or datetime.now().date()
        return U.TIMEZONE_OFFSETS[tz].localize(
            datetime(
                _date.year,
                _date.month,
                _date.day,
                view.value[0].value,
                view.value[1].value
            )
        )

################################################################################
    async def set_start_time(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Setting start time for ShiftBracket {self.id}")

        prompt = U.make_embed(
            title="__Set Start Time__",
            description="Please select the start time for this shift bracket."
        )

        start_dt = await self.get_single_time(
            interaction, prompt, self._parent.start_time.date(), self._parent.timezone
        )
        if start_dt is None:
            log.debug(self.guild, "Start time not set")
            return

        # If the selected start time is earlier than the event start time, it means the shift starts on the next day
        if start_dt.time() < self._parent.start_time.time():
            log.info(self.guild, "Shift starts on the next day")
            start_dt += timedelta(days=1)

        self.start_time = start_dt

        log.info(self.guild, f"Shift start time set to {self.start_time}")

################################################################################
    async def set_end_time(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Setting end time for ShiftBracket {self.id}")

        prompt = U.make_embed(
            title="__Set End Time__",
            description="Please select the end time for this shift bracket."
        )

        end_dt = await self.get_single_time(
            interaction, prompt, self._parent.start_time.date(), self._parent.timezone
        )
        if end_dt is None:
            log.debug(self.guild, "End time not set")
            return

        if end_dt.time() < self._parent.start_time.time():
            log.info(self.guild, "Shift ends on the next day")
            end_dt += timedelta(days=1)

        self.end_time = end_dt

        log.info(self.guild, f"Shift end time set to {self.end_time}")

################################################################################
    async def remove(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Removing ShiftBracket {self.id}")

        prompt = U.make_embed(
            title="__Remove Shift Bracket__",
            description=(
                f"Are you sure you want to remove the shift bracket for "
                f"{U.format_dt(self.start_time, 't')} - {U.format_dt(self.end_time, 't')}?"
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "ShiftBracket removal cancelled")
            return

        self.delete()

        log.info(self.guild, f"ShiftBracket {self.id} removed")

################################################################################
    def field_header(self) -> str:

        return (
            f"__**{U.format_dt(self._start, 't')} - "
            f"{U.format_dt(self._end, 't')}**__"
        )

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "id": self.id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }

################################################################################

