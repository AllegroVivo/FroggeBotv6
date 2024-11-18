from __future__ import annotations

from datetime import datetime, timedelta, UTC, time
from typing import TYPE_CHECKING, List, Optional, Dict, Type, TypeVar, Any

from discord import (
    User,
    Embed,
    Message,
    EmbedField,
    Interaction,
    Thread,
    ChannelType,
    Forbidden,
    SelectOption,
    NotFound, HTTPException,
)
from discord.ext.pages import Page

from Assets import BotEmojis
from Classes.Common import ManagedObject, LazyMessage
from Enums import ElementType
from Enums import Minutes, Hours
from Errors import InvalidNumber, ChannelNotSet, InsufficientPermissions
from UI.Common import FroggeSelectView, BasicNumberModal, FroggeMultiMenuSelect
from UI.Events import (
    EventStatusView,
    ShiftBracketMenuStatusView,
    ShiftBracketTimeSelectView,
    EventPositionsStatusView,
    EventSignupView,
    EventListView,
    EventStaffManagementView,
    EventTemplateView,
    EventPositionSelectView,
)
from Utilities import Utilities as U
from logger import log
from .EventDetails import EventDetails
from .EventPosition import EventPosition
from .EventSignup import EventSignup
from .ShiftBracket import ShiftBracket

if TYPE_CHECKING:
    from Classes import EventManager, EventElement, StaffMember
    from UI.Common import FroggeView
################################################################################

__all__ = ("Event", )

E = TypeVar("E", bound="Event")

################################################################################
class Event(ManagedObject):

    __slots__ = (
        "_details",
        "_shifts",
        "_positions",
        "_post_msg",
        "_is_template",
    )

################################################################################
    def __init__(self, mgr: EventManager, _id: int, **kwargs) -> None:

        super().__init__(mgr, _id)

        self._details: EventDetails = EventDetails(self, **kwargs)
        self._shifts: List[ShiftBracket] = kwargs.get("shifts", [])
        self._positions: List[EventPosition] = kwargs.get("positions", [])
        self._is_template: bool = kwargs.get("is_template", False)

        self._post_msg: LazyMessage = LazyMessage(self, kwargs.get("post_url"))

################################################################################
    @classmethod
    def new(cls: Type[E], mgr: EventManager) -> E:

        new_data = mgr.bot.api.create_event(mgr.guild_id)
        return cls(mgr, new_data["id"])

################################################################################
    @classmethod
    def load(cls: Type[E], mgr: EventManager, data: Dict[str, Any]) -> E:

        self: E = cls.__new__(cls)

        self._id = data["id"]
        self._mgr = mgr

        self._details = EventDetails.load(self, data)
        self._shifts = [ShiftBracket.load(self, s) for s in data["shift_brackets"]]
        self._positions = [EventPosition.load(self, p) for p in data["positions"]]
        self._is_template = data.get("is_template", False)

        self._post_msg = LazyMessage(self, data.get("post_url"))

        return self

################################################################################
    @classmethod
    def copy(cls: Type[E], template: Event) -> Event:

        # Call the API to create a new event for the template data
        new_event = cls.new(template._mgr)  # type: ignore

        # Transfer the relevant details from the template to the new event
        new_event._details = EventDetails.copy(new_event, template)
        new_event._shifts = [ShiftBracket.copy(new_event, s) for s in template._shifts]
        new_event._positions = [EventPosition.copy(new_event, p) for p in template._positions]

        new_event.update()
        return new_event

################################################################################
    @property
    def name(self) -> Optional[str]:

        return self._details.name

################################################################################
    @property
    def description(self) -> Optional[str]:

        return self._details.description

################################################################################
    @property
    def start_time(self) -> Optional[datetime]:

        return self._details.start_time

################################################################################
    @property
    def end_time(self) -> Optional[datetime]:

        return self._details.end_time

################################################################################
    @property
    def image(self) -> Optional[str]:

        return self._details.image

################################################################################
    @property
    def elements(self) -> Dict[ElementType, List[EventElement]]:

        return self._details.elements

################################################################################
    @property
    def positions(self) -> List[EventPosition]:

        return self._positions

################################################################################
    @property
    def shifts(self) -> List[ShiftBracket]:

        return self._shifts

################################################################################
    @property
    async def post_message(self) -> Optional[Message]:

        return await self._post_msg.get()

    @post_message.setter
    def post_message(self, value: Message) -> None:

        self._post_msg.set(value)

################################################################################
    @property
    def is_template(self) -> bool:

        return self._is_template

    @is_template.setter
    def is_template(self, value: bool) -> None:

        self._is_template = value
        self.update()

################################################################################
    @property
    def signups(self) -> List[EventSignup]:

        return [
            signup for pos in self.positions
            for signup in pos.signups
        ]

################################################################################
    @property
    def is_locked_out(self) -> bool:

        if self.start_time is None:
            return False

        return self.start_time - timedelta(minutes=self._mgr.lockout_threshold) < datetime.now(UTC)  # type: ignore

################################################################################
    @property
    def staff(self) -> List[StaffMember]:

        return [signup.staff_member for signup in self.signups]

################################################################################
    def get_bracket(self, bracket_id: int) -> Optional[ShiftBracket]:

        return next((b for b in self._shifts if b.id == int(bracket_id)), None)

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_event(self.id)
        self.manager._managed.remove(self)

################################################################################
    def update(self) -> None:

        self.bot.api.update_event(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        ret = {
            "name": self.name,
            "description": self.description,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "image_url": self.image,
            "post_url": self._post_msg.id,
            "is_template": self.is_template,
        }

        return ret

################################################################################
    async def status(self) -> Embed:

        start_time = (
            U.format_dt(self.start_time, "f")
            if self.start_time
            else "`Not Set`"
        )
        end_time = (
            U.format_dt(self.end_time, "f")
            if self.end_time
            else "`Not Set`"
        )

        pos_list = "\n* ".join(
            [
                f"{pos.emoji if pos.emoji else ''} {pos.position.name} - {pos.quantity}x"
                for pos in self.positions
            ]
        )
        pos_list = (
            "`No Positions Selected Yet`"
            if not pos_list
            else "* " + pos_list
        )

        shift_value = "`No Shift Brackets Set Up`"
        if self.shifts:
            shift_value = "* " + "\n* ".join(
                [
                    f"{U.format_dt(s.start_time, 't')} - "
                    f"{(U.format_dt(s.end_time, 't'))}" for s in self.shifts
                ]
            )

        shift_emoji = BotEmojis.Check if self.is_fully_covered() else BotEmojis.Cross
        shift_coverage_str = (
            "`Shifts Match Event Time`"
            if self.is_fully_covered()
            else "`Missing Shift Time(s)`"
        )

        post_message = await self.post_message
        return U.make_embed(
            title=f"__{self.name}__",
            description=(
                (
                    f"{str(BotEmojis.ArrowRight)} "
                    f"[Posted - See It Here]({post_message.jump_url}) "
                    f"{str(BotEmojis.ArrowLeft)}"
                )
                if post_message
                else "`Not Posted Yet`"
            ) + f"\n{U.draw_line(extra=17)}" + (
                f"\n**Is Template:** `{self.is_template}`"
            ),
            footer_text=f"ID: {self.id}",
            thumbnail_url=self.image,
            fields=[
                EmbedField(
                    name="__Event Hours__",
                    value=f"{start_time} - {end_time}",
                    inline=False
                ),
                EmbedField(
                    name="__Shift Brackets__",
                    value=(
                        f"{str(shift_emoji)} {shift_coverage_str} {str(shift_emoji)}\n"
                        f"{shift_value}"
                    ),
                    inline=False
                ),
                EmbedField(
                    name="__Positions Required__",
                    value=pos_list,
                    inline=False
                ),
                EmbedField(
                    name="__Secondary Elements__",
                    value=(
                          f"**[{sum(len(v) for v in self.elements.values())}]** "
                          "element(s) attached to this event."
                    ) + f"\n{U.draw_line(extra=25)}",
                    inline=False
                )
            ] + [await p.event_field() for p in self.positions]
        )

################################################################################
    async def template_status(self) -> Embed:

        start_time = (
            U.format_dt(self.start_time, "t")
            if self.start_time
            else "`Not Set`"
        )
        end_time = (
            U.format_dt(self.end_time, "t")
            if self.end_time
            else "`Not Set`"
        )

        pos_list = "\n* ".join(
            [
                f"{pos.emoji if pos.emoji else ''} {pos.position.name} - {pos.quantity}x"
                for pos in self.positions
            ]
        ) if self.positions else "`No Positions Selected Yet`"

        shift_value = "`No Shift Brackets Set Up`"
        if self.shifts:
            shift_value = "* " + "\n* ".join(
                [
                    f"{U.format_dt(s.start_time, 't')} - "
                    f"{(U.format_dt(s.end_time, 't'))}" for s in self.shifts
                ]
            )

        shift_emoji = BotEmojis.Check if self.is_fully_covered() else BotEmojis.Cross
        shift_coverage_str = (
            "`Shifts Match Event Time`"
            if self.is_fully_covered()
            else "`Missing Shift Time(s)`"
        )

        return U.make_embed(
            title=f"__{self.name}__",
            footer_text=f"ID: {self.id}",
            thumbnail_url=self.image,
            fields=[
                EmbedField(
                    name="__Event Hours__",
                    value=f"{start_time} - {end_time}",
                    inline=False
                ),
                EmbedField(
                    name="__Shift Brackets__",
                    value=(
                        f"{str(shift_emoji)} {shift_coverage_str} {str(shift_emoji)}\n"
                        f"{shift_value}"
                    ),
                    inline=False
                ),
                EmbedField(
                    name="__Positions Required__",
                    value=pos_list,
                    inline=False
                ),
                EmbedField(
                    name="__Secondary Elements__",
                    value=(
                        f"**[{sum(len(v) for v in self.elements.values())}]** "
                        "element(s) attached to this event."
                    ) + f"\n{U.draw_line(extra=25)}",
                    inline=False
                )
            ] + [await p.event_field() for p in self.positions]
        )

################################################################################
    async def compile(self) -> List[Embed]:

        start_time = (
            U.format_dt(self.start_time, "f")
            if self.start_time
            else "`Not Set`"
        )
        end_time = (
            U.format_dt(self.end_time, "f")
            if self.end_time
            else "`Not Set`"
        )

        pos_list = "\n* ".join(
            [
                f"{pos.emoji if pos.emoji else ''} {pos.position.name} - {pos.quantity}x"
                for pos in self.positions
            ]
        )
        pos_list = (
            "`No Positions Selected Yet`"
            if not pos_list
            else "* " + pos_list
        )

        main_event_embed = U.make_embed(
            title=f"__{self.name}__",
            footer_text=f"ID: {self.id}",
            thumbnail_url=self.image,
            fields=[
                EmbedField(
                    name="__Event Hours__",
                    value=f"{start_time} - {end_time}",
                    inline=False
                ),
                EmbedField(
                    name="__Positions Required__",
                    value=pos_list + f"\n{U.draw_line(extra=30)}",
                    inline=False
                ),
            ] + [await p.event_field() for p in self.positions]
        )
        ret = [main_event_embed]

        for _type in self.elements:
            element_str = ""
            for element in self.elements[_type]:
                element_str += (
                    f"**{element.title}:**\n"
                    f"```{element.value}```\n\n"
                )
            element_embed = U.make_embed(
                title=f"__{_type.proper_name}__",
                description=element_str,
            )
            ret.append(element_embed)

        return ret

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return EventStatusView(user, self)

################################################################################
    def is_fully_covered(self) -> bool:

        if self.start_time is None or self.end_time is None:
            return False

        start_time_with_tz = U.ensure_timezone(self.start_time, self.timezone)
        end_time_with_tz = U.ensure_timezone(self.end_time, self.timezone)

        # Adjust end time if it is on the next day
        if end_time_with_tz < start_time_with_tz:
            end_time_with_tz += timedelta(days=1)

        event_duration = int((end_time_with_tz - start_time_with_tz).total_seconds() / 60)
        total_shift_length = sum(bracket.length for bracket in self.shifts)

        return total_shift_length >= event_duration

################################################################################
    async def set_name(self, interaction: Interaction) -> None:

        await self._details.set_name(interaction)

################################################################################
    async def set_description(self, interaction: Interaction) -> None:

        await self._details.set_description(interaction)

################################################################################
    async def set_start_time(self, interaction: Interaction) -> None:

        await self._details.set_start_time(interaction)

################################################################################
    async def set_end_time(self, interaction: Interaction) -> None:

        await self._details.set_end_time(interaction)

################################################################################
    async def set_image(self, interaction: Interaction) -> None:

        await self._details.set_image(interaction)

################################################################################
    def shift_bracket_status(self) -> Embed:

        shift_value = "`No Shift Brackets Set Up`"
        if self.shifts:
            shift_value = "\n".join(
                [
                    f"* {U.format_dt(shift.start_time, 't')} - "
                    f"{(U.format_dt(shift.end_time, 't'))}"
                    for shift in self.shifts
                ]
            )

        shift_emoji = BotEmojis.Check if self.is_fully_covered() else BotEmojis.Cross
        shift_coverage_str = (
            "`Shifts Match Event Time`"
            if self.is_fully_covered()
            else "`Missing Shift Time(s)`"
        )

        return U.make_embed(
            title="Shift Bracket Menu",
            fields=[
                EmbedField(
                    name="__Event Hours:__",
                    value=(
                        f"**Start Time:** "
                        f"{U.format_dt(self.start_time, 'f') if self.start_time else 'Not Set'}\n"
                        f"**End Time:** "
                        f"{U.format_dt(self.end_time, 'f') if self.end_time else 'Not Set'}"
                    ),
                    inline=False
                ),
                EmbedField(
                    name="__Current Shift Brackets:__",
                    value=(
                        f"{str(shift_emoji)} {shift_coverage_str} {str(shift_emoji)}\n"
                        f"{shift_value}"
                    ),
                    inline=False
                )
            ]
        )

################################################################################
    async def shift_bracket_menu(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Opening shift bracket menu for event {self.name} ({self.id}).")

        embed = self.shift_bracket_status()
        view = ShiftBracketMenuStatusView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def add_shift_bracket(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Adding shift bracket to event {self.name} ({self.id}).")

        if not (self.start_time and self.end_time):
            log.warning(self.guild, f"Missing event times for event {self.name} ({self.id}).")
            error = U.make_error(
                title="Missing Event Times",
                message=(
                    "You can't proceed with this action because the event's "
                    "start and/or end times are missing."
                ),
                solution=(
                    "Please set the event's start and end times before "
                    "attempting to perform this action."
                )
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        localized_start_dt = self.start_time.astimezone(self.py_tz)
        localized_end_dt = self.end_time.astimezone(self.py_tz)

        event_start_time = localized_start_dt.time()
        event_end_time = localized_end_dt.time()

        if event_start_time < event_end_time:
            hours_list = [
                i for i
                in range(event_start_time.hour, event_end_time.hour + 1)
            ]
        else:
            hours_list = (
                [i for i in range(event_start_time.hour, 24)] +
                [i for i in range(0, event_end_time.hour + 1)]
            )

        base_hour_options = Hours.select_options()
        start_hour_options = []

        for option in base_hour_options:
            if int(option.value) in hours_list:
                start_hour_options.append(option)

        prompt = U.make_embed(
            title="Select Start Time",
            description=(
                "Please select the start time for the new shift bracket."
            )
        )

        view = ShiftBracketTimeSelectView(
            owner=interaction.user,
            hours=start_hour_options,
            minutes=Minutes.select_options()
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "Shift bracket creation cancelled.")
            return

        shift_start_hour, shift_start_minute = view.value
        shift_start_time = time(shift_start_hour.value, shift_start_minute.value)

        log.info(self.guild, f"Shift start time selected: {shift_start_time}.")

        prompt = U.make_embed(
            title="Select End Time",
            description=(
                "Please select the end time for the new shift bracket."
            )
        )
        view = ShiftBracketTimeSelectView(interaction.user, start_hour_options, Minutes.select_options())

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "Shift bracket creation cancelled.")
            return

        shift_end_hour, shift_end_minute = view.value
        shift_end_time = time(shift_end_hour.value, shift_end_minute.value)

        log.info(self.guild, f"Shift end time selected: {shift_end_time}.")

        # Handle the start date and end date correctly when the event spans midnight
        start_date = localized_start_dt.date()

        if shift_start_time < event_start_time:
            shift_start_date = start_date + timedelta(days=1)
        else:
            shift_start_date = start_date

        if shift_end_time < event_start_time:
            shift_end_date = start_date + timedelta(days=1)
        else:
            shift_end_date = start_date

        new_bracket = ShiftBracket.new(
            parent=self,
            start_time=self.py_tz.localize(
                datetime(
                    year=shift_start_date.year,
                    month=shift_start_date.month,
                    day=shift_start_date.day,
                    hour=shift_start_time.hour,
                    minute=shift_start_time.minute
                )
            ),
            end_time=self.py_tz.localize(
                datetime(
                    year=shift_end_date.year,
                    month=shift_end_date.month,
                    day=shift_end_date.day,
                    hour=shift_end_time.hour,
                    minute=shift_end_time.minute
                )
            )
        )

        if any(bracket.overlaps_with(new_bracket) for bracket in self.shifts):
            log.warning(self.guild, "Conflicting shift bracket detected.")
            error = U.make_error(
                title="Conflicting Shift Bracket",
                description=(
                    f"**Problem Range:** "
                    f"{U.format_dt(new_bracket.start_time, 't')} - "
                    f"{U.format_dt(new_bracket.end_time, 't')}"
                ),
                message=(
                    "The shift bracket you are trying to create conflicts with "
                    "another shift bracket or the start/end of the event."
                ),
                solution=(
                    "Ensure the shift bracket you are trying to create does not "
                    "conflict with any other shift bracket or the start/end times "
                    "of the event."
                )
            )
            new_bracket.delete()
            await interaction.respond(embed=error, ephemeral=True)
            return

        self._shifts.append(new_bracket)

        log.info(self.guild, f"Shift bracket added to event {self.name} ({self.id}).")

################################################################################
    def get_shift_bracket(self, bracket_id: int) -> Optional[ShiftBracket]:

        return next((s for s in self.shifts if s.id == int(bracket_id)), None)

################################################################################
    async def modify_shift_bracket(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Modifying shift bracket for event {self.name} ({self.id}).")

        prompt = U.make_embed(
            title="Select Shift Bracket",
            description="Please select the shift bracket you would like to modify."
        )
        options = [bracket.select_option() for bracket in self.shifts]
        view = FroggeSelectView(interaction.user, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "Shift bracket modification cancelled.")
            return

        bracket = self.get_shift_bracket(view.value)
        log.info(self.guild, f"Modifying shift bracket {bracket.id}.")

        await bracket.menu(interaction)

################################################################################
    async def remove_shift_bracket(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Removing shift bracket for event {self.name} ({self.id}).")

        prompt = U.make_embed(
            title="Select Shift Bracket",
            description="Please select the shift bracket you would like to remove."
        )
        options = [bracket.select_option() for bracket in self.shifts]
        view = FroggeSelectView(interaction.user, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "Shift bracket removal cancelled.")
            return

        bracket = self.get_shift_bracket(view.value)
        log.info(self.guild, f"Removing shift bracket {bracket.id}.")

        await bracket.remove(interaction)

################################################################################
    def positions_status(self) -> Embed:

        pos_list = "\n* ".join(
            [
                f"{str(pos.emoji) if pos.emoji else ''} {pos.position.name} - {pos.quantity}x"
                for pos in self.positions
            ]
        )
        pos_list = (
            "`No Positions Selected Yet`"
            if not pos_list
            else "* " + pos_list
        )

        return U.make_embed(
            title="Positions Menu",
            fields=[
                EmbedField(
                    name="__Positions Required__",
                    value=pos_list + f"\n{U.draw_line(extra=25)}",
                    inline=False
                )
            ]
        )

################################################################################
    async def positions_menu(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Opening positions menu for event {self.name} ({self.id}).")

        embed = self.positions_status()
        view = EventPositionsStatusView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def add_position(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Adding position to event {self.name} ({self.id}).")

        prompt = U.make_embed(
            title="__Select Position(s)__",
            description="Please select the position(s) you would like to add to the event."
        )
        view = EventPositionSelectView(interaction.user, self)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "Position addition cancelled.")
            return

        pos_ids, quantity = view.value

        for pos_id in pos_ids:
            pos = self._mgr.guild.position_manager[pos_id]
            log.info(self.guild, f"Adding position {pos.name} to event {self.name} ({self.id}).")  # type: ignore
            self._positions.append(EventPosition.new(self, pos, quantity))  # type: ignore

################################################################################
    async def modify_position(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Modifying position for event {self.name} ({self.id}).")

        raw_options = self._mgr.guild.position_manager.select_options()
        options = [
            o
            for o in raw_options
            if int(o.value) in [p.position.id for p in self.positions]
        ]
        if not options:
            log.debug(self.guild, "No positions available to modify.")
            options.append(SelectOption(label="No Positions Available", value="-1"))

        prompt = U.make_embed(
            title="__Select Position(s)__",
            description="Please select the position(s) to edit."
        )
        view = FroggeSelectView(interaction.user, options, multi_select=True, return_interaction=True)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "Position modification cancelled.")
            return

        pos_ids, inter = view.value
        log.info(self.guild, f"Modifying positions {pos_ids} for event {self.name} ({self.id}).")

        modal = BasicNumberModal(
            title="Staff Needed",
            attribute="Staff Needed",
            example="eg. '2'",
            max_length=1
        )

        await inter.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            log.debug(self.guild, "Position modification cancelled.")
            return

        try:
            quantity = int(modal.value)
        except ValueError:
            log.warning(self.guild, f"Invalid number '{modal.value}'.")
            error = InvalidNumber(modal.value)
            await interaction.respond(embed=error, ephemeral=True)
            return

        for pos_id in pos_ids:
            self.get_position(pos_id).quantity = quantity

        log.info(self.guild, f"Positions {pos_ids} to quantity {quantity} for event {self.name} ({self.id}).")

################################################################################
    def get_position(self, pos_id: int) -> Optional[EventPosition]:

        return next((p for p in self.positions if p.position.id == int(pos_id)), None)

################################################################################
    async def remove_position(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Removing position for event {self.name} ({self.id}).")

        raw_options = self._mgr.guild.position_manager.select_options()
        options = [
            o
            for o in raw_options
            if int(o.value) in [p.position.id for p in self.positions]
        ]
        if not options:
            log.debug(self.guild, "No positions available to remove.")
            options.append(SelectOption(label="No Positions Available", value="-1"))

        prompt = U.make_embed(
            title="__Select Position(s)__",
            description="Please select the position(s) to remove."
        )
        view = FroggeSelectView(interaction.user, options, multi_select=True)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "Position removal cancelled.")
            return

        log.info(self.guild, f"Removing positions {view.value} for event {self.name} ({self.id}).")

        for pos_id in view.value:
            self.get_position(pos_id).delete()

        log.info(self.guild, "Successfully removed positions.")

################################################################################
    async def post(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Posting event {self.name} ({self.id}).")

        channel = await self.manager.channel  # type: ignore
        if channel is None:
            log.warning(self.guild, "Scheduling channel not set.")
            error = ChannelNotSet("Scheduling")
            await interaction.respond(embed=error, ephemeral=True)
            return

        if await self.update_post_components() is True:
            return

        view = EventSignupView(self)
        self.bot.add_view(view)

        confirm = U.make_embed(
            title="__Event Posted__",
            description=(
                "Your event has been successfully posted/updated in "
                "the scheduling channel."
            )
        )

        if channel.type is ChannelType.text:
            log.info(self.guild, "Posting event to text channel.")
            self.post_message = await channel.send(embeds=await self.compile(), view=view)
            await interaction.respond(embed=confirm)
            return

        log.info(self.guild, "Posting event to forum channel.")

        name_string = f"{self.name.lower()} - {self.start_time.date().strftime('%m/%d')}"
        matching_thread = next((t for t in channel.threads if t.name.lower() == name_string), None)
        tags = []

        if matching_thread:
            # Clear the matching thread
            await matching_thread.edit(applied_tags=tags)
            action = matching_thread.send  # type: ignore
        else:
            # Or create a new thread if no matching one
            action = lambda **kw: channel.create_thread(name=name_string, applied_tags=tags, **kw)  # type: ignore

        # Post or create thread and handle permissions error
        try:
            result = await action(embeds=await self.compile(), view=view)
            if isinstance(result, Thread):
                self.post_message = await result.fetch_message(result.last_message_id)
            else:
                self.post_message = result
        except Forbidden:
            log.warning(self.guild, "Insufficient permissions to post event.")
            error = InsufficientPermissions(channel, "Send Messages")
            await interaction.respond(embed=error, ephemeral=True)
        else:
            await interaction.respond(embed=self.success_message())

################################################################################
    async def update_post_components(self) -> bool:

        if await self.post_message is None:
            return False

        view = EventSignupView(self)
        self.bot.add_view(view)

        try:
            post_message = await self.post_message
            await post_message.edit(embeds=await self.compile(), view=view)
        except NotFound:
            self.post_message = None
            return False
        except HTTPException:
            log.warning(self.guild, "Failed to update event post.")
            return False
        else:
            return True

################################################################################
    def success_message(self) -> Embed:

        return U.make_embed(
            title="Event Posted",
            description=(
                "Your event has been successfully posted/updated "
                "in the scheduling channel. [View it here!]("
                f"{self._post_msg.id})"
            )
        )

################################################################################
    async def secondary_element_menu(self, interaction) -> None:

        await self._details.secondary_element_menu(interaction)

################################################################################
    async def mark_template(self, interaction: Interaction) -> None:

        self.is_template = not self.is_template
        await interaction.respond("** **", delete_after=0.1)

################################################################################
    async def page(self) -> Page:

        return Page(embeds=[await self.status()], custom_view=EventListView(self))

################################################################################
    async def template_page(self) -> Page:

        return Page(embeds=[await self.template_status()], custom_view=EventTemplateView(self))

################################################################################
    async def staff_member_status(self) -> Embed:

        return U.make_embed(
            title="Staff Member Menu",
            description=(
                "Please select an option from the menu below\n"
                "to manually edit staff for this event.\n"
                f"{U.draw_line(extra=27)}"
            ),
            fields=[await p.event_field() for p in self.positions]
        )

################################################################################
    async def manual_staff_edit(self, interaction: Interaction) -> None:

        status = await self.staff_member_status()
        view = EventStaffManagementView(interaction.user, self)

        await interaction.respond(embed=status, view=view)
        await view.wait()

################################################################################
    async def add_staff_manual(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Adding staff manually to event {self.name} ({self.id}).")

        options = [
            SelectOption(label=p.position.name, value=str(p.position.id))
            for p in self.positions
            if not p.is_full
        ]
        if not options:
            log.debug(self.guild, "No positions available to add staff.")
            options.append(SelectOption(label="No Positions Available", value="-1"))

        prompt = U.make_embed(
            title="__Select Position__",
            description="Please select the position(s) to add staff to."
        )
        view = FroggeSelectView(interaction.user, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "Staff addition cancelled.")
            return

        position = self.get_position(int(view.value))
        log.info(self.guild, f"Adding staff to positions {position.id} for event {self.name} ({self.id}).")

        available_shifts = []
        for pos in self.positions:
            if pos.position.id == position.position.id:
                available_shifts = pos.get_available_shifts()
                break

        assert available_shifts, "No available shifts found for selected position."

        prompt = U.make_embed(
            title="__Select Shift__",
            description="Please select the shift to add staff to."
        )
        view = FroggeSelectView(interaction.user, [s.select_option() for s in available_shifts])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "Staff addition cancelled.")
            return

        bracket = self.get_shift_bracket(int(view.value))

        base_staff = self.guild.staff_manager.can_work_position(position.position.id)
        staff_options = [
            s.select_option()
            for s in base_staff
            if s not in bracket.staff
        ]

        if not staff_options:
            staff_options.append(SelectOption(
                label="No Staff Available",
                value="-1",
            ))

        prompt = U.make_embed(
            title="__Select Staff__",
            description="Please select the staff member to add to the shift."
        )
        view = FroggeSelectView(interaction.user, staff_options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "Staff addition cancelled.")
            return

        staff = self.guild.staff_manager.get_by_id(int(view.value))
        position.signups.append(EventSignup.new(position, staff, bracket))

        log.info(self.guild, f"Staff added to position {position.id} for event {self.name} ({self.id}).")

################################################################################
    async def remove_staff_manual(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Removing staff manually from event {self.name} ({self.id}).")

        options = [
            SelectOption(label=p.position.name, value=str(p.position.id))
            for p in self.positions
            if p.signups
        ]
        if not options:
            log.debug(self.guild, "No positions available to remove staff.")
            options.append(SelectOption(label="No Positions Available", value="-1"))

        prompt = U.make_embed(
            title="__Select Position__",
            description="Please select the position(s) to remove staff from."
        )
        view = FroggeSelectView(interaction.user, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "Staff removal cancelled.")
            return

        position = self.get_position(int(view.value))
        log.info(self.guild, f"Removing staff from positions {position.id} for event {self.name} ({self.id}).")

        staff_options = [
            s.select_option()
            for s in position.signups
        ]

        if not staff_options:
            staff_options.append(SelectOption(
                label="No Staff Available",
                value="-1",
            ))

        staff_options.sort(key=lambda x: x.description)

        prompt = U.make_embed(
            title="__Select Staff__",
            description="Please select the staff member to remove from the position."
        )
        view = FroggeMultiMenuSelect(interaction.user, None, staff_options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "Staff removal cancelled.")
            return

        signup = next((s for s in position.signups if s.id == int(view.value)), None)
        log.info(self.guild, f"Removing staff {signup.staff_member.id} from position {position.id} for event {self.name} ({self.id}).")

        signup.delete()

################################################################################
    async def process_employee_punch(self, interaction: Interaction) -> None:

        await self.guild.punch_manager.process_punch_in(interaction, self)

################################################################################
