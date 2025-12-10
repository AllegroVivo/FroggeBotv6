from __future__ import annotations

from datetime import datetime, UTC
from typing import TYPE_CHECKING, Optional, List, Dict, Type, TypeVar, Any

from discord import Interaction, Embed, EmbedField, SelectOption

from Enums import ElementType
from Errors import MaxItemsReached
from UI.Common import FroggeSelectView, DateTimeModal, BasicTextModal
from UI.Events import EventElementMenuView
from Utilities import Utilities as U
from logger import log
from .EventElement import EventElement

if TYPE_CHECKING:
    from Classes import Event, EventTemplate, FroggeBot, GuildData
################################################################################

__all__ = ("EventDetails", )

ED = TypeVar("ED", bound="EventDetails")

################################################################################
class EventDetails:

    __slots__ = (
        "_parent",
        "_name",
        "_description",
        "_start",
        "_end",
        "_image",
        "_elements",
    )

    MAX_ELEMENT_COUNT = 20

################################################################################
    def __init__(self, parent: Event, **kwargs) -> None:

        self._parent: Event = parent

        self._name: Optional[str] = kwargs.get("name")
        self._description: Optional[str] = kwargs.get("description")
        self._start: Optional[datetime] = kwargs.get("start_time")
        self._end: Optional[datetime] = kwargs.get("end_time")
        self._image: Optional[str] = kwargs.get("image_url")
        self._elements: Dict[ElementType, List[EventElement]] = kwargs.get("elements", {})

################################################################################
    @classmethod
    def load(cls: Type[ED], parent: Event, data: Dict[str, Any]) -> ED:

        self: ED = cls.__new__(cls)

        self._parent = parent

        self._name = data["name"]
        self._description = data["description"]
        self._start = datetime.fromisoformat(data["start_time"]) if data["start_time"] else None
        self._end = datetime.fromisoformat(data["end_time"]) if data["end_time"] else None
        self._image = data["image_url"]

        element_dict = {}

        for item in data["secondary_elements"]:
            key = ElementType(item["element_type"])
            if key not in element_dict:
                element_dict[key] = []
            element_dict[key].append(EventElement.load(parent, item))

        self._elements = element_dict

        return self

################################################################################
    @classmethod
    def copy(cls: Type[ED], parent: Event, template: Event) -> ED:

        if template.start_time and template.end_time:
            now = datetime.now(UTC)
            start_day = end_day = now.day
            if template.end_time.time() < template.start_time.time():
                end_day += 1

            start_time = template.start_time.replace(month=now.month, day=start_day, year=now.year)
            end_time = template.end_time.replace(month=now.month, day=end_day, year=now.year)
        else:
            start_time = end_time = None

        self: ED = cls.__new__(cls)

        self._parent = parent

        self._name = template.name
        self._description = template.description
        self._start = start_time
        self._end = end_time
        self._image = template.image

        self._elements = {}
        for element in template._details.elements.items():
            self._elements[element[0]] = [EventElement.copy(parent, e) for e in element[1]]

        return self

################################################################################
    @property
    def bot(self) -> FroggeBot:

        return self._parent.bot

################################################################################
    @property
    def parent(self) -> Event:

        return self._parent

################################################################################
    @property
    def guild(self) -> GuildData:

        return self._parent.manager.guild

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
    def description(self) -> Optional[str]:

        return self._description

    @description.setter
    def description(self, value: str) -> None:

        self._description = value
        self.update()

################################################################################
    @property
    def start_time(self) -> Optional[datetime]:

        return self._start

    @start_time.setter
    def start_time(self, value: datetime) -> None:

        self._start = value
        self.update()

################################################################################
    @property
    def end_time(self) -> Optional[datetime]:

        return self._end

    @end_time.setter
    def end_time(self, value: datetime) -> None:

        self._end = value
        self.update()

################################################################################
    @property
    def image(self) -> Optional[str]:

        return self._image

    @image.setter
    def image(self, value: str) -> None:

        self._image = value
        self.update()

################################################################################
    @property
    def elements(self) -> Dict[ElementType, List[EventElement]]:

        return self._elements

################################################################################
    def update(self) -> None:

        self._parent.update()

################################################################################
    async def set_name(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Setting event name for {self.name}")

        modal = BasicTextModal(
            title="Enter Event Name",
            attribute="Name",
            cur_val=self.name,
            example="e.g. 'Tuesday Night Opening'",
            max_length=60,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            log.debug(self.guild, "Event name modal was not completed.")
            return

        self.name = modal.value

        log.info(self.guild, f"Event name set to '{self.name}'")

################################################################################
    async def set_description(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Setting event description for {self.name}")

        modal = BasicTextModal(
            title="Enter Event Description",
            attribute="Description",
            cur_val=self.description,
            max_length=200,
            required=False,
            multiline=True
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            log.debug(self.guild, "Event description modal was not completed.")
            return

        self.description = modal.value

        log.info(self.guild, f"Event description set to '{self.description}'")

################################################################################
    async def set_start_time(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Setting event start time for {self.name}")

        start_time = (
            self._parent.py_tz.localize(self.start_time)
            if self.start_time is not None
            and self.start_time.tzinfo is None
            else None
        )

        modal = DateTimeModal("Event Start Time", start_time)

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            log.debug(self.guild, "Event start time modal was not completed.")
            return

        localized = self._parent.py_tz.localize(modal.value)
        self.start_time = localized

        log.info(self.guild, f"Event start time set to '{self.start_time}'")

################################################################################
    async def set_end_time(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Setting event end time for {self.name}")

        end_time = (
            self._parent.py_tz.localize(self.end_time)
            if self.end_time is not None
            and self.end_time.tzinfo is None
            else None
        )

        modal = DateTimeModal("Event End Time", end_time)

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            log.debug(self.guild, "Event end time modal was not completed.")
            return

        localized = self._parent.py_tz.localize(modal.value)

        if self.start_time is not None:
            if localized <= U.ensure_timezone(self.start_time, self._parent.timezone):
                log.warning(
                    self.guild,
                    f"Event end time ({localized}) is before event "
                    f"start time ({self.start_time})."
                )
                error = U.make_error(
                    title="Invalid Event Datetime Entry",
                    message="The end time cannot be before or equal to the start time.",
                    solution=(
                        "Please correct the end time so that it is after the start time."
                    )
                )
                await interaction.respond(embed=error, ephemeral=True)
                return

        self.end_time = localized

        log.info(self.guild, f"Event end time set to '{self.end_time}'")

################################################################################
    async def set_image(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Setting event image for {self.name}")

        prompt = U.make_embed(
            title="Set Event Image",
            description="Please send the image you want to use for the event in this channel now.",
        )

        if image := await U.wait_for_image(interaction, prompt):
            self.image = image
            log.info(self.guild, f"Event image set to '{self.image}'")

################################################################################
    def secondary_element_status(self) -> Embed:

        return U.make_embed(
            title="__Event Secondary Elements__",
            description=(
                f"Currently attached secondary elements for this event: "
                f"**[{len(self.elements)}]**"
            ),
            fields=[
                EmbedField(
                    name=f"{ElementType(key).proper_name} Elements",
                    value="\n".join([element.title for element in value]),
                    inline=True,
                )
                for key, value in self.elements.items()
            ],
        )

################################################################################
    async def secondary_element_menu(self, interaction: Interaction) -> None:

        embed = self.secondary_element_status()
        view = EventElementMenuView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    def secondary_element_options(self) -> List[SelectOption]:

        ret = []

        for _type, elements in self.elements.items():
            for element in elements:
                ret.append(
                    SelectOption(
                        label=element.title,
                        description=U.string_clamp(element.value or "", 50),
                        value=str(element.id)
                    )
                )

        return ret

################################################################################
    def get_secondary_element(self, element_id: int) -> Optional[EventElement]:

        return next((element for elements in self.elements.values() for element in elements if element.id == int(element_id)), None)

################################################################################
    async def add_secondary_element(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Adding secondary element to {self.name}")

        if len(self.elements) > self.MAX_ELEMENT_COUNT:
            log.warning(self.guild, "Max secondary elements reached.")
            error = MaxItemsReached("Event Elements", self.MAX_ELEMENT_COUNT)
            await interaction.respond(embed=error, ephemeral=True)
            return

        prompt = U.make_embed(
            title="__Add Secondary Element__",
            description="Please select the type of secondary element you would like to add.",
        )
        view = FroggeSelectView(owner=interaction.user,  options=ElementType.select_options())

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "Secondary element selection was not completed.")
            return

        element_type = ElementType(int(view.value))

        new_element = EventElement.new(self.parent, element_type)
        if element_type not in self.elements:
            self.elements[element_type] = []
        self.elements[element_type].append(new_element)

        log.info(self.guild, f"Secondary element '{element_type.proper_name}' added to {self.name}")

        await new_element.menu(interaction)

################################################################################
    async def modify_secondary_element(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Modifying secondary element for {self.name}")

        prompt = U.make_embed(
            title="__Modify Secondary Element__",
            description="Please select the secondary element you would like to modify.",
        )
        view = FroggeSelectView(owner=interaction.user, options=self.secondary_element_options())

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "Secondary element selection was not completed.")
            return

        element = self.get_secondary_element(view.value)
        log.info(self.guild, f"Modifying secondary element '{element.title}' for {self.name}")

        await element.menu(interaction)

################################################################################
    async def remove_secondary_element(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Removing secondary element from {self.name}")

        prompt = U.make_embed(
            title="__Remove Secondary Element__",
            description="Please select the secondary element you would like to remove.",
        )

        view = FroggeSelectView(owner=interaction.user, options=self.secondary_element_options())

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            log.debug(self.guild, "Secondary element selection was not completed.")
            return

        element = self.get_secondary_element(view.value)
        log.info(self.guild, f"Removing secondary element '{element.title}' from {self.name}")

        await element.remove(interaction)

################################################################################
