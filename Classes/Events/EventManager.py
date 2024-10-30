from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, List, Dict, Optional, Union

from discord import Interaction, User, Embed, TextChannel, ForumChannel, ChannelType, NotFound

from Classes.Common import ObjectManager, LazyChannel
from .Event import Event

from Utilities import Utilities as U
from UI.Events import (
    EventManagerStatusView,
    EventListFrogginator
)
from logger import log
from UI.Common import BasicTextModal, InstructionsInfo, ConfirmCancelView

if TYPE_CHECKING:
    from Classes import GuildData, Position
    from UI.Common import FroggeView
################################################################################

__all__ = ("EventManager", )

################################################################################
class EventManager(ObjectManager):

    __slots__ = (
        "_lockout",
        "_templates",
        "_channel",
    )

################################################################################
    def __init__(self, state: GuildData) -> None:

        super().__init__(state)

        self._lockout: int = 0
        self._channel: LazyChannel = LazyChannel(self, None)

################################################################################
    async def load_all(self, payload: Dict[str, Any]) -> None:

        self._lockout = payload["event_lockout"]
        self._managed = [Event.load(self, e) for e in payload["events"]]
        self._channel = LazyChannel(self, payload["channel_id"])

        for event in self._managed:
            await event.update_post_components()

################################################################################
    @property
    def events(self) -> List[Event]:

        return self._managed  # type: ignore

################################################################################
    @property
    def lockout_threshold(self) -> int:

        return self._lockout

    @lockout_threshold.setter
    def lockout_threshold(self, value: int) -> None:

        self._lockout = value
        self.update()

################################################################################
    @property
    def templates(self) -> List[Event]:

        return [e for e in self._managed if e.is_template]  # type: ignore

################################################################################
    @property
    async def channel(self) -> Optional[Union[TextChannel, ForumChannel]]:

        return await self._channel.get()

    @channel.setter
    def channel(self, value: Union[TextChannel, ForumChannel]) -> None:

        self._channel.set(value)

################################################################################
    @property
    def current_event(self) -> Optional[Event]:

        now = datetime.now()
        for event in self.events:
            if not (event.start_time or event.end_time):
                continue
            if event.start_time - timedelta(minutes=30) <= now <= event.end_time + timedelta(hours=8):
                return event

################################################################################
    def update(self) -> None:

        self.bot.api.update_event_system(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "event_lockout": self._lockout,
            "channel_id": self._channel.id,
        }

################################################################################
    async def status(self) -> Embed:

        channel = await self.channel
        return U.make_embed(
            title="__Events Module Status__",
            description=(
                f"__**Schedule Lockout Threshold:**__ "
                f"`{self.lockout_threshold} min.` prior to event\n\n"

                f"__**Scheduling Channel:**__ "
                f"{'`Not Set`' if channel is None else channel.mention}\n\n"

                f"**[`{len(self.events)}`]** events are currently scheduled.\n"
                f"**[`{len(self.templates)}`]** event templates are available.\n\n"

                "Please select a button below to add or modify events."
            )
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return EventManagerStatusView(user, self)

################################################################################
    async def add_item(self, interaction: Interaction) -> None:

        log.info(self.guild, "Adding New Event")

        event = Event.new(self)
        self.events.append(event)

        log.info(self.guild, f"New Event ID: {event.id}")

        await event.menu(interaction)

################################################################################
    async def modify_item(self, interaction: Interaction) -> None:

        log.info(self.guild, "Modifying Event")

        modal = BasicTextModal(
            title="Enter Event ID",
            attribute="Event ID",
            example="e.g. '12345'",
            max_length=8,
            required=True,
            instructions=InstructionsInfo(
                placeholder="Enter the event ID",
                value=(
                    "Enter the ID number for the event you wish to edit. This can "
                    "be found at the bottom of all event-related messages."
                )
            )
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            log.debug(self.guild, "Event ID Modal Cancelled")
            return

        log.info(self.guild, f"Modifying Event ID: {modal.value}")

        event = self[modal.value]
        if event is None:
            log.warning(self.guild, f"Invalid Event ID: {modal.value}")
            error = U.make_error(
                title="Invalid Event ID Number",
                description=f"Invalid Value: {modal.value}",
                message="The event ID you entered is invalid.",
                solution=(
                    "Please make sure you are entering the correct event ID number. "
                    "This is located at the bottom of all event-related messages."
                )
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        log.info(self.guild, f"Event Found: {event.name}")

        await event.menu(interaction)

################################################################################
    async def remove_item(self, interaction: Interaction) -> None:

        log.info(self.guild, "Removing Event")

        modal = BasicTextModal(
            title="Enter Event ID",
            attribute="Event ID",
            example="e.g. '12345'",
            max_length=8,
            required=True,
            instructions=InstructionsInfo(
                placeholder="Enter the event ID",
                value=(
                    "Enter the ID number for the event you wish to edit. This can "
                    "be found at the bottom of all event-related messages."
                )
            )
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            log.debug(self.guild, "Event ID Modal Cancelled")
            return

        log.info(self.guild, f"Deleting Event ID: {modal.value}")

        event: Event = self[modal.value]  # type: ignore
        if event is None:
            log.warning(self.guild, f"Invalid Event ID: {modal.value}")
            error = U.make_error(
                title="Invalid Event ID Number",
                description=f"Invalid Value: {modal.value}",
                message="The event ID you entered is invalid.",
                solution=(
                    "Please make sure you are entering the correct event ID number. "
                    "This is located at the bottom of all event-related messages."
                )
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        log.info(self.guild, f"Event Found: {event.name}. Confirming Deletion...")

        prompt = U.make_embed(
            title="Confirm Event Deletion",
            description=(
                f"Are you sure you want to delete the event __**{event.name}**__?\n\n"

                "This action cannot be undone."
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "Event Deletion Cancelled")
            return

        if event._post_msg.id is not None:
            try:
                post_message = await event.post_message
                if post_message is not None:
                    await post_message.delete()
            except NotFound:
                pass

        event.delete()

        log.info(self.guild, f"Event Deleted: {event.name}")

################################################################################
    async def events_list(self, interaction: Interaction) -> None:

        log.info(self.guild, "Displaying Event List")

        pages = [await event.page() for event in self.events]

        frogginator = EventListFrogginator(pages, self)
        await frogginator.respond(interaction)

################################################################################
    async def set_lockout(self, interaction: Interaction) -> None:

        log.info(self.guild, "Setting Schedule Lockout Threshold")

        modal = BasicTextModal(
            title="Set Schedule Lockout",
            attribute="Lockout (in Minutes)",
            cur_val=str(self.lockout_threshold),
            example="e.g. '120'",
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            log.debug(self.guild, "Schedule Lockout Modal Cancelled")
            return

        self.lockout_threshold = modal.value

        log.info(self.guild, f"Schedule Lockout Threshold Set: {modal.value} min.")

################################################################################
    async def set_scheduling_channel(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Scheduling Channel__",
            description=(
                "Please select the channel where event scheduling messages will be sent."
            )
        )
        channel = await U.select_channel(
            interaction=interaction,
            guild=self.guild,
            channel_type="Scheduling Channel",
            channel_prompt=prompt
        )
        if channel is None:
            return

        self.channel = channel

################################################################################
    async def view_event_templates(self, interaction: Interaction) -> None:

        log.info(self.guild, "Displaying Event Templates")

        pages = [await event.template_page() for event in self.templates]
        if not pages:
            error = U.make_error(
                title="No Templates Available",
                message="There are no event templates available to display.",
                solution="Please create a new template before proceeding."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        frogginator = EventListFrogginator(pages, self)
        await frogginator.respond(interaction)

################################################################################
    def get_template(self, template_id: str) -> Optional[Event]:

        for template in self.templates:
            if template.id == template_id:
                return template

################################################################################
    async def create_event_from_template(self, interaction: Interaction, template: Event) -> None:

        await interaction.response.defer(invisible=False)

        new_event = Event.from_template(self, template)
        new_event.update()  # Call this so the event's datetimes are saved to the database
        self.events.append(new_event)

        await new_event.menu(interaction)

################################################################################
    async def remove_position(self, position: Position) -> None:

        pass

################################################################################
