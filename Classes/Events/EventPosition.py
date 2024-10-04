from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Type, TypeVar, Dict, Any, Tuple

from discord import PartialEmoji, EmbedField, Interaction, SelectOption

from Classes.Common import Identifiable
from .EventSignup import EventSignup
from UI.Common import FroggeSelectView
from Utilities import Utilities as U
from .TemplatePosition import TemplatePosition

if TYPE_CHECKING:
    from Classes import Event, Position, FroggeBot, ShiftBracket
################################################################################

__all__ = ("EventPosition", )

EP = TypeVar("EP", bound="EventPosition")

################################################################################
class EventPosition(Identifiable):

    __slots__ = (
        "_parent",
        "_pos",
        "_qty",
        "_signups",
        "_emoji",
    )

################################################################################
    def __init__(self, parent: Event, _id: int, **kwargs) -> None:

        super().__init__(_id)

        self._parent: Event = parent

        self._pos: Position = kwargs.pop("position")
        self._qty: int = kwargs.get("quantity", 1)
        self._signups: List[EventSignup] = kwargs.get("signups", [])
        self._emoji: Optional[PartialEmoji] = kwargs.get("emoji", None)

################################################################################
    @classmethod
    def new(cls: Type[EP], parent: Event, pos: Position, qty: int) -> EP:

        new_data = parent.bot.api.create_event_position(parent.id, pos.id, qty)
        return cls(parent, new_data["id"], position=pos, quantity=qty)

################################################################################
    @classmethod
    def load(cls: Type[EP], parent: Event, data: Dict[str, Any]) -> EP:

        self: EP = cls.__new__(cls)

        self._id = data["id"]
        self._parent = parent

        self._pos = parent.guild.position_manager[data["position_id"]]
        self._qty = data["quantity"]
        self._emoji = PartialEmoji.from_str(data["emoji"]) if data["emoji"] else None

        self._signups = [EventSignup.load(self, s) for s in data["signups"]]

        return self

################################################################################
    @classmethod
    def from_template(cls: Type[EP], parent: Event, other: TemplatePosition) -> EP:

        new_data = parent.bot.api.create_event_position(parent.id, other.position.id, other.quantity)
        return cls(
            parent=parent,
            _id=new_data["id"],
            pos=parent.guild.position_manager[other.position_id],
            quantity=other.quantity,
        )

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
    def position(self) -> Position:

        return self._pos

################################################################################
    @property
    def quantity(self) -> int:

        return self._qty

    @quantity.setter
    def quantity(self, value: int) -> None:

        self._qty = value
        self.update()

################################################################################
    @property
    def signups(self) -> List[EventSignup]:

        return self._signups

################################################################################
    @property
    def emoji(self) -> Optional[PartialEmoji]:

        return self._emoji

    @emoji.setter
    def emoji(self, value: Optional[PartialEmoji]) -> None:

        self._emoji = value
        self.update()

################################################################################
    @property
    def is_full(self) -> bool:

        return all([len(self.get_signups_by_bracket(b)) == self.quantity for b in self._parent.shifts])

################################################################################
    def update(self) -> None:

        self.bot.api.update_event_position(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "position_id": self.position.id,
            "quantity": self.quantity,
            "emoji": str(self.emoji) if self.emoji else None,
        }

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_event_position(self.id)
        self._parent.positions.remove(self)

################################################################################
    async def event_field(self) -> EmbedField:

        emoji = str(self.emoji) if self.emoji else ""
        value = ""
        for bracket in self._parent.shifts:
            value += f"{bracket.field_header()}\n"
            signups = []
            for s in self.signups:
                if s.bracket == bracket:
                    signups.append(s)
            # signups = [s for s in self.signups if s.bracket == bracket]
            for i in range(self.quantity):
                try:
                    user = await signups[i].staff_member.user
                    shift_str = user.mention
                except IndexError:
                    shift_str = "`Available`"
                value += f"> {shift_str}\n"

        if not value:
            value = "`Not Set Up Yet`"

        return EmbedField(
            name=f"{emoji} {self.position.name} - ({self.quantity}x)",
            value=value,
            inline=True
        )

################################################################################
    def get_signups_by_bracket(self, bracket: ShiftBracket) -> List[EventSignup]:

        return [s for s in self.signups if s.bracket == bracket]

################################################################################
    async def toggle_user_signup(self, interaction: Interaction) -> None:

        staff = self.parent.manager.guild.staff_manager[interaction.user.id]
        if staff is None:
            error = U.make_error(
                title="User Not Registered",
                message=f"{interaction.user.mention} is not registered as a staff member.",
                solution="Please hire this user before proceeding."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        if self.position not in staff.positions:
            error = U.make_error(
                title="Not Qualified",
                message=f"You are not qualified to take a shift of the type `{self.position.name}`.",
                solution="Please contact a member of the staff team for assistance."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        signups = [s for s in self.signups if s.staff_member == staff]
        if signups:
            for signup in signups:
                signup.delete()

            await interaction.respond("** **", delete_after=0.1)
            return

        options = [
            s.select_option()
            for s in self.parent.shifts
            if self.quantity > len(self.get_signups_by_bracket(s))
        ]
        if not options:
            options.append(
                SelectOption(
                    label="No Shifts Available",
                    value="-1",
                )
            )

        prompt = U.make_embed(
            title="Select a Shift Bracket",
            description="Please select one or more shift(s) to sign up for",
        )
        view = FroggeSelectView(
            owner=interaction.user,
            options=options,
            multi_select=True,
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        shifts = [self.parent.get_bracket(bracket_id) for bracket_id in view.value]
        for shift in shifts:
            self.signups.append(EventSignup.new(self, staff, shift))

        await self._parent.update_post_components()

################################################################################
    def _add_signup_from_data(self, data: Dict[str, Any]) -> None:

        self._signups.append(EventSignup.load(self, data))

################################################################################
    def get_available_shifts(self) -> List[ShiftBracket]:

        return [s for s in self._parent.shifts if self.quantity > len(self.get_signups_by_bracket(s))]

################################################################################
