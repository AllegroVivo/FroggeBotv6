from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Type, TypeVar, Any, Dict, Optional

from discord import User, Embed, EmbedField, Interaction, File, Message, NotFound, ChannelType, Forbidden

from Classes.Common import LazyMessage
from Classes.Activities import BaseActivity
from .RaffleDetails import RaffleDetails
from .RaffleEntry import RaffleEntry
from Utilities import Utilities as U
from Assets import BotEmojis
from UI.Raffles import RaffleStatusView
from Errors import NoEntries, ChannelMissing, InsufficientPermissions
from UI.Common import ConfirmCancelView

if TYPE_CHECKING:
    from Classes import RaffleManager
    from UI.Common import FroggeView
################################################################################

__all__ = ("Raffle", )

R = TypeVar("R", bound="Raffle")

################################################################################
class Raffle(BaseActivity):

    __slots__ = (
        "_active",
        "_post_msg",
    )

################################################################################
    def __init__(self, mgr: RaffleManager, _id: int, **kwargs) -> None:

        details = kwargs.get("details") or RaffleDetails(self)
        entries = kwargs.get("entries") or []
        winners = kwargs.get("winners") or []

        super().__init__(mgr, _id, details, entries, winners)

        self._active = kwargs.get("is_active", False)
        self._post_msg = LazyMessage(self, kwargs.get("post_url"))

################################################################################
    @classmethod
    def new(cls: Type[R], mgr: RaffleManager) -> R:

        is_active = len(mgr.active_items) == 0
        new_data = mgr.bot.api.create_raffle(mgr.guild_id, is_active)

        return cls(mgr, new_data["id"], active=is_active)

################################################################################
    @classmethod
    def load(cls: Type[R], mgr: RaffleManager, data: Dict[str, Any]) -> R:

        self: R = cls.__new__(cls)

        self._id = data["id"]
        self._mgr = mgr

        self._details = RaffleDetails.load(self, data["details"])
        self._entries = [RaffleEntry.load(self, e) for e in data["entries"]]
        self._winners = [e for e in self._entries if e.id in data["winners"]]

        self._active = data["is_active"]
        self._post_msg = LazyMessage(self, data["post_url"])

        return self

################################################################################
    @property
    def cost(self) -> int:

        return self._details.cost  # type: ignore

################################################################################
    @property
    def total_tickets(self) -> int:

        return sum(e.quantity for e in self._entries)

################################################################################
    @property
    def total_cost(self) -> int:

        return self.total_tickets * self.cost

################################################################################
    @property
    async def post_message(self) -> Optional[Message]:

        return await self._post_msg.get()

    @post_message.setter
    def post_message(self, value: Message) -> None:

        self._post_msg.set(value)

################################################################################
    def update(self) -> None:

        self.bot.api.update_raffle(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "winners": [e.id for e in self._winners],
            "is_active": self._active,
            "post_url": self._post_msg.id
        }

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_raffle(self.id)
        self._mgr._managed.remove(self)

################################################################################
    async def status(self) -> Embed:

        return U.make_embed(
            title=f"__{self.name or 'Raffle Status'}__",
            description=(
                f"**[`{self.total_tickets}`]** tickets sold\n"
                f"**[`{self.total_cost:,}`]** gil in the pot"
            ),
            fields=[
                EmbedField(
                    name="__Num. Winners__",
                    value=f"`{self.num_winners}x winner(s)`",
                    inline=True
                ),
                EmbedField(
                    name="__Prize Split__",
                    value=(
                        f"{self._details.winner_pct}/{self._details.venue_pct}\n"  # type: ignore
                        f"*(winner/venue)*"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__Notify Winner__",
                    value=str(BotEmojis.Check if self.auto_notify else BotEmojis.Cross),
                    inline=True
                ),
                EmbedField(
                    name="__Cost per Ticket__",
                    value=f"`{self.cost:,} gil` / ticket",
                    inline=True
                ),
                EmbedField(
                    name="__Is Active__",
                    value=str(BotEmojis.Check if self._active else BotEmojis.Cross),
                    inline=True
                ),
            ]
        )

################################################################################
    def tracker(self) -> Embed:

        return U.make_embed(
            title=f"__{self.name or 'Raffle Status'}__",
            description=(
                f"**[`{self.total_tickets}`]** tickets sold\n"
                f"**[`{self.total_cost:,}`]** gil in the pot"
            ),
            fields=[
                EmbedField(
                    name="__Cost per Ticket__",
                    value=f"`{self.cost:,} gil` / ticket",
                    inline=False
                ),
                EmbedField(
                    name="__Prize Split__",
                    value=(
                        f"{self._details.winner_pct}/{self._details.venue_pct}\n"  # type: ignore
                        f"*(winner/venue)*"
                    ),
                    inline=True
                ),
            ]
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return RaffleStatusView(user, self)

################################################################################
    async def determine_winners(self, interaction) -> None:

        if not self._entries:
            error = NoEntries("Raffle")
            await interaction.respond(embed=error, ephemeral=True)
            return

        await super().determine_winners(interaction)
        await self.guild.log.activity_rolled(self, interaction.user)

        await interaction.respond("** **", delete_after=0.1)

################################################################################
    async def set_cost(self, interaction: Interaction) -> None:

        await self._details.set_cost(interaction)  # type: ignore

################################################################################
    async def toggle_active(self, interaction: Interaction) -> None:

        # If we're toggling this raffle on, turn off all other raffles
        if not self._active:
            if self._mgr.active_raffle is not None:  # type: ignore
                prompt = U.make_embed(
                    title="__Raffle Already Active__",
                    description=(
                        "There is already an active raffle in progress.\n"
                        "Would you like to deactivate it?\n\n"

                        "*(This will prevent users from purchasing tickets\n"
                        "but won't affect already-purchased entries.)*"
                    )
                )
                view = ConfirmCancelView(interaction.user)

                await interaction.respond(embed=prompt, view=view)
                await view.wait()

                if not view.complete or view.value is False:
                    return

            for raffle in self._mgr.active_items:  # type: ignore
                if raffle._active:  # type: ignore
                    raffle.set_active(False)  # type: ignore

        self.set_active(not self._active)

        await interaction.respond("** **", delete_after=0.1)

################################################################################
    def set_active(self, active: bool) -> None:

        self._active = active
        self.update()

################################################################################
    async def add_tickets(self, interaction: Interaction, user: User, qty: int) -> None:

        if entry := self[user.id]:
            await entry.add_tickets(interaction, qty)  # type: ignore
        else:
            entry = RaffleEntry.new(self, user.id, qty)
            self._entries.append(entry)

        await self.update_post_components()

        confirm = U.make_embed(
            title="__Tickets Added__",
            description=(
                f"Successfully added **`{qty}`** tickets to the raffle "
                f"`{self.name}` for {user.mention}!"
            )
        )
        await interaction.respond(embed=confirm, ephemeral=True)

################################################################################
    async def entries_report(self, interaction: Interaction) -> None:

        entry_data = await self.generate_entries_report_str()
        filename = f"{self.name or 'Unnamed Raffle'} Entries - {datetime.now().strftime('%m-%d-%y')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(entry_data)

        await interaction.respond(file=File(filename))

################################################################################
    async def post_tracker(self, interaction: Interaction) -> None:

        if await self.update_post_components():
            return

        prompt = U.make_embed(
            title="__Post Tracking Message__",
            description=(
                "Please enter a mention of the channel you would you like to post "
                "a tracking message in to track the status of this raffle?\n\n"
                
                "*(This message will be updated automatically as tickets are added.)*"
            )
        )
        channel = await U.listen_for(interaction, prompt, U.MentionableType.Channel, [ChannelType.text])
        if channel is None:
            return

        try:
            self.post_message = await channel.send(embed=self.tracker())
        except NotFound:
            self.post_message = None
            error = ChannelMissing()
            await interaction.respond(embed=error, ephemeral=True)
        except Forbidden:
            error = InsufficientPermissions(channel, "Send Messages")
            await interaction.respond(embed=error, ephemeral=True)
        else:
            await interaction.respond("**Tracker Posted**")

################################################################################
    async def update_post_components(self) -> bool:

        if (await self.post_message) is None:
            return False

        try:
            await (await self.post_message).edit(embed=self.tracker())
        except NotFound:
            self.post_message = None
            return False
        else:
            return True

################################################################################
