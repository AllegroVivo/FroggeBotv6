from __future__ import annotations

from datetime import datetime, UTC
from typing import TYPE_CHECKING, Type, TypeVar, Any, Dict, Optional

from discord import (
    User,
    Embed,
    Message,
    PartialEmoji,
    TextChannel,
    EmbedField,
    Interaction,
    NotFound,
    Forbidden,
)
from discord.ext.pages import Page

from Assets import BotEmojis
from Classes.Activities import BaseActivity
from Classes.Common import LazyMessage
from Errors import ChannelNotSet, ChannelMissing, InsufficientPermissions
from UI.Common import ConfirmCancelView
from UI.Giveaways import GiveawayStatusView, GiveawaySignupView
from Utilities import Utilities as U, FroggeColor
from .GiveawayDetails import GiveawayDetails
from .GiveawayEntry import GiveawayEntry

if TYPE_CHECKING:
    from Classes import GiveawayManager
    from UI.Common import FroggeView
################################################################################

__all__ = ("Giveaway", )

G = TypeVar("G", bound="Giveaway")

################################################################################
class Giveaway(BaseActivity):

    __slots__ = (
        "_post_msg",
    )

################################################################################
    def __init__(self, mgr: GiveawayManager, _id: int, **kwargs) -> None:

        details = kwargs.get("details") or GiveawayDetails(self)
        entries = kwargs.get("entries", [])
        winners = kwargs.get("winners", [])

        super().__init__(mgr, _id, details, entries, winners)

        self._post_msg: LazyMessage = LazyMessage(self, kwargs.get("post_url"))

################################################################################
    @classmethod
    def new(cls: Type[G], mgr: GiveawayManager) -> G:

        new_data = mgr.bot.api.create_giveaway(mgr.guild_id)
        return cls(mgr, new_data["id"])

################################################################################
    @classmethod
    def load(cls: Type[G], mgr: GiveawayManager, data: Dict[str, Any]) -> G:

        self: G = cls.__new__(cls)

        self._id = data["id"]
        self._mgr = mgr

        self._details = GiveawayDetails.load(self, data["details"])
        self._entries = [GiveawayEntry.load(self, entry) for entry in data["entries"]]
        self._winners = [e for e in self._entries if e.id in data["winners"]]

        self._post_msg = LazyMessage(self, data["post_url"])

        return self

################################################################################
    @property
    async def post_message(self) -> Optional[Message]:

        return await self._post_msg.get()

    @post_message.setter
    def post_message(self, value: Optional[Message]) -> None:

        self._post_msg.set(value)

################################################################################
    @property
    def description(self) -> Optional[str]:

        return self._details.description  # type: ignore

################################################################################
    @property
    def thumbnail(self) -> Optional[str]:

        return self._details.thumbnail  # type: ignore

################################################################################
    @property
    def color(self) -> Optional[FroggeColor]:

        return self._details.color  # type: ignore

################################################################################
    @property
    def end_date(self) -> Optional[datetime]:

        return self._details.end  # type: ignore

################################################################################
    @property
    def emoji(self) -> Optional[PartialEmoji]:

        return self._details.emoji  # type: ignore

################################################################################
    @property
    async def post_channel(self) -> Optional[TextChannel]:

        return await self._mgr.channel

################################################################################
    def is_active(self) -> bool:

        return len(self.winners) == 0

################################################################################
    def update(self) -> None:

        self.bot.api.update_giveaway(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "winners": [w.id for w in self.winners],
            "post_url": self._post_msg.id
        }

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_giveaway(self.id)
        self._mgr._managed.remove(self)

################################################################################
    async def status(self) -> Embed:

        winner_list = [await e.user for e in self.winners]
        return U.make_embed(
            color=self.color or FroggeColor.embed_background(),
            title="__Giveaway Details__",
            description=(
                f"**Giveaway Name:** {self.name or '`Not Set`'}\n"
                f"**Description:**\n```{self.description or 'Not Set'}```\n"
                f"{U.draw_line(extra=30)}"
            ),
            fields=[
                EmbedField(
                    name="__Accent Color__",
                    value=(
                        f"{BotEmojis.ArrowLeft} -- (__{str(self.color).upper()}__)"
                        if self.color is not None
                        else "`Not Set`"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__Button Emoji__",
                    value=(
                        str(self.emoji)
                        if self.emoji is not None
                        else f"`Not Set` ({str(BotEmojis.PartyPopper)})"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__Prize__",
                    value=self.prize or "`Not Set`",
                    inline=True
                ),
                EmbedField(
                    name="__End Date__",
                    value=(
                        f"{U.format_dt(self.end_date, 'f')}\n({U.format_dt(self.end_date, 'R')})"
                        if self.end_date
                        else "`Not Set`"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__Auto-Notify__",
                    value=str(BotEmojis.Check if self.auto_notify else BotEmojis.Cross),
                    inline=True
                ),
                EmbedField(
                    name="** **",
                    value=(
                        f"**Number of Winners:** **[`{self.num_winners}`]**\n"
                        f"**Winners:** {', '.join(user.mention for user in winner_list) if winner_list else '`None Yet`'}"
                    ),
                    inline=False
                )
            ],
            thumbnail_url=self.thumbnail,
            footer_text=f"Giveaway ID: {self.id}"
        )

################################################################################
    async def compile(self) -> Embed:

        winner_list = [await e.user for e in self.winners]
        return U.make_embed(
            color=self.color or FroggeColor.embed_background(),
            title=self.name,
            description=(
                f"```{self.description}```"
                if self.description is not None
                else None
            ),
            fields=[
                EmbedField(
                    name="__Prize__",
                    value=(
                        self.prize
                        if self.prize is not None
                        else "`No Prize Set`"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__End Date__",
                    value=(
                        f"{U.format_dt(self.end_date, 'f')} "
                        f"({U.format_dt(self.end_date, 'R')})"
                    ) if self.end_date else "`No End Date Set`",
                    inline=False
                ),
                EmbedField(
                    name="** **",
                    value=(
                        f"**Number of Winners:** **[`{self.num_winners}`]**\n"
                        f"**Number of Entries:** {len(self.entries)}\n" +
                        (
                            f"**Winners:** "
                            f"{', '.join(user.mention for user in winner_list)}"
                            if self.winners
                            else ""
                        )
                    ),
                    inline=False
                )
            ],
            thumbnail_url=self.thumbnail,
            footer_text=f"Giveaway ID: {self.id}"
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return GiveawayStatusView(user, self)

################################################################################
    async def set_description(self, interaction: Interaction) -> None:

        await self._details.set_description(interaction)  # type: ignore

################################################################################
    async def set_thumbnail(self, interaction: Interaction) -> None:

        await self._details.set_thumbnail(interaction)  # type: ignore

################################################################################
    async def set_color(self, interaction: Interaction) -> None:

        await self._details.set_color(interaction)  # type: ignore

################################################################################
    async def set_end_date(self, interaction: Interaction) -> None:

        await self._details.set_end_date(interaction)  # type: ignore

################################################################################
    async def set_emoji(self, interaction: Interaction) -> None:

        await self._details.set_emoji(interaction)  # type: ignore

################################################################################
    async def post(self, interaction: Interaction) -> None:

        if await self.update_post_components():
            success = U.make_embed(
                title="__Giveaway Posted__",
                description=(
                    f"The giveaway has been successfully updated.\n"
                    f"[Click here to view the post.]({self._post_msg.id})"
                )
            )
            await interaction.respond(embed=success)
            return

        post_channel = await self.post_channel
        if post_channel is None:
            error = ChannelNotSet("Giveaways")
            await interaction.respond(embed=error, ephemeral=True)
            return

        if not await self.update_post_components():
            view = GiveawaySignupView(self)
            self.bot.add_view(view)

            try:
                self.post_message = await post_channel.send(embed=await self.compile(), view=view)
            except NotFound:
                error = ChannelMissing()
                await interaction.respond(embed=error, ephemeral=True)
                return
            except Forbidden:
                error = InsufficientPermissions(post_channel, "Send Messages")
                await interaction.respond(embed=error, ephemeral=True)
                return

        success = U.make_embed(
            title="__Giveaway Posted__",
            description=(
                f"The giveaway has been successfully posted in "
                f"{post_channel.mention}."
            )
        )
        await interaction.respond(embed=success)

################################################################################
    async def update_post_components(self, force: bool = False) -> bool:

        if self.winners and not force:
            return True

        if await self.post_message is None:
            return False

        if not force:
            view = GiveawaySignupView(self)
            self.bot.add_view(view)
        else:
            view = None

        try:
            post_message = await self.post_message
            await post_message.edit(embed=await self.compile(), view=view)
        except NotFound:
            self.post_message = None
            return False
        else:
            return True

################################################################################
    async def determine_winners(self, interaction: Interaction) -> None:

        if self.end_date and U.ensure_timezone(self.end_date, self.timezone) > datetime.now(UTC):
            warning = U.make_embed(
                title="__Giveaway Still Active__",
                description=(
                    "The giveaway has not ended yet.\n"
                    "Are you sure you want to determine the winners early?"
                )
            )
            view = ConfirmCancelView(interaction.user)

            await interaction.respond(embed=warning, view=view)
            await view.wait()

            if not view.complete or view.value is False:
                return

        await super().determine_winners(interaction)
        await self.guild.log.activity_rolled(self, interaction.user)

        await self.update_post_components(force=True)
        await interaction.respond("** **", delete_after=0.1)

################################################################################
    async def signup(self, interaction: Interaction) -> None:

        if self.winners:
            await interaction.respond("The giveaway has already ended.", ephemeral=True)
            return

        if entry := self.get_entry_by_user(interaction.user.id):
            entry.delete()
            confirm = U.make_embed(
                title="__Giveaway Entry Removed__",
                description="You have successfully removed your entry."
            )
        else:
            new_entry = GiveawayEntry.new(self, interaction.user)
            self._entries.append(new_entry)
            confirm = U.make_embed(
                title="__Giveaway Entry Added__",
                description="You have successfully entered the giveaway."
            )

        await interaction.respond(embed=confirm, ephemeral=True)

################################################################################
    def get_entry_by_user(self, user_id: int) -> Optional[GiveawayEntry]:

        return next((e for e in self.entries if e._user.id == int(user_id)), None)

################################################################################
    async def page(self) -> Page:

        return Page(embeds=[await self.status()])

################################################################################
