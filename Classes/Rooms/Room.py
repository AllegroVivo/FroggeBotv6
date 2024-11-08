from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional, List, Type, TypeVar, Any, Dict

from discord import (
    User,
    Embed,
    EmbedField,
    PartialEmoji,
    Interaction,
    SelectOption,
    NotFound,
    Forbidden,
    Message,
)

from Assets import BotEmojis
from Classes.Common import ManagedObject, LazyMessage
from .RoomDetails import RoomDetails
from Utilities import Utilities as U
from UI.Rooms import RoomStatusView, RoomReservationView
from UI.Common import FroggeSelectView
from .RoomImage import RoomImage
from Errors import MaxItemsReached, ChannelMissing, InsufficientPermissions

if TYPE_CHECKING:
    from Classes import RoomsManager
    from UI.Common import FroggeView
################################################################################

__all__ = ("Room", )

R = TypeVar("R", bound="Room")

################################################################################
class Room(ManagedObject):

    __slots__ = (
        "_details",
        "_images",
        "_post_msg",
        "_in_use",
        "_occupant",
        "_end_dt",
    )

    MAX_IMAGES = 10

################################################################################
    def __init__(self, mgr: RoomsManager, _id: int, index: int, **kwargs) -> None:

        super().__init__(mgr, _id)

        self._details: RoomDetails = kwargs.get("details", RoomDetails(self, index))
        self._images: List[RoomImage] = kwargs.get("images", [])
        self._post_msg: LazyMessage = LazyMessage(self, kwargs.get("post_url"))

        self._in_use: bool = False
        self._occupant: Optional[User] = None
        self._end_dt: Optional[datetime] = None

################################################################################
    @classmethod
    def new(cls: Type[R], mgr: RoomsManager, index: int) -> R:

        new_data = mgr.bot.api.create_room(mgr.guild_id, index)
        return cls(mgr, new_data["id"], index)

################################################################################
    @classmethod
    def load(cls: Type[R], mgr: RoomsManager, data: Dict[str, Any]) -> R:

        self: R = cls.__new__(cls)

        self._id = data["id"]
        self._mgr = mgr

        self._details = RoomDetails.load(self, data["details"])
        self._images = [RoomImage.load(self, i) for i in data["images"]]
        self._post_msg = LazyMessage(self, data["post_message"])

        self._in_use = False
        self._occupant = None
        self._end_dt = None

        return self

################################################################################
    @property
    def index(self) -> int:

        return self._details.index

################################################################################
    @property
    async def owner(self) -> Optional[User]:

        return await self._details.owner

################################################################################
    @property
    def theme(self) -> Optional[str]:

        return self._details.theme

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
    def locked(self) -> bool:

        return self._details.locked

################################################################################
    @property
    def emoji(self) -> Optional[PartialEmoji]:

        return self._details.emoji

################################################################################
    @property
    def disabled(self) -> bool:

        return self._details.disabled

################################################################################
    @property
    def images(self) -> List[RoomImage]:

        return self._images

################################################################################
    @property
    async def post_message(self) -> Optional[Message]:

        return await self._post_msg.get()

    @post_message.setter
    def post_message(self, value: Optional[Message]) -> None:

        self._post_msg.set(value)

################################################################################
    def update(self) -> None:

        self.bot.api.update_room(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "post_message": self._post_msg.id,
        }

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_room(self.id)
        self._mgr._managed.remove(self)

################################################################################
    async def status(self) -> Embed:

        description = (
            f"Room `{self.index:03d}` "
            f"is currently `{'in use' if self._in_use else 'available'}`.\n"
        )
        if self._in_use:
            description += (
                f"Occupant: {self._occupant or '`None`'}\n"
                f"End Time: {self._end_dt or '`Not Set`'}\n"
            )

        owner = await self.owner
        return U.make_embed(
            title=f"__Room Status__",
            description=description,
            image_url=self.images[0].url if self.images else None,
            fields=[
                EmbedField(
                    name="__Name__",
                    value=self.name or "`Not Set`",
                    inline=True
                ),
                EmbedField(
                    name="__Owner__",
                    value=owner.mention if owner else "`Not Set`",
                    inline=True
                ),
                EmbedField(
                    name="__Theme__",
                    value=self.theme or "`Not Set`",
                    inline=True
                ),
                EmbedField(
                    name="__Description__",
                    value=f"```{self.description or 'Not Set'}```",
                    inline=False
                ),
                EmbedField(
                    name="__Locked__",
                    value=str(BotEmojis.CheckGreen if self.locked else BotEmojis.Cross),
                    inline=True
                ),
                EmbedField(
                    name="__Disabled__",
                    value=str(BotEmojis.CheckGreen if self.disabled else BotEmojis.Cross),
                    inline=True
                ),
                EmbedField(
                    name="__Emoji__",
                    value=str(self.emoji) or "`Not Set`",
                    inline=True
                ),
                EmbedField(
                    name="__Images__",
                    value=f"`{len(self._images)}x`",
                    inline=False
                ),
            ]
        )

################################################################################
    async def compile(self) -> Embed:

        fields = []
        if self.theme is not None:
            fields.append(
                EmbedField(
                    name="__Theme__",
                    value=f"```{self.theme}```",
                    inline=False
                )
            )

        fields += [
            EmbedField(
                name=f"{BotEmojis.Silhouette} __Owner__",
                value=(await self.owner).mention if await self.owner else "`Not Set`",
                inline=True
            ),
            EmbedField(
                name=(
                    f"{BotEmojis.Lock} __Locked__ {BotEmojis.Lock}"
                    if self.locked
                    else f"{BotEmojis.Unlock} __Unlocked__ {BotEmojis.Unlock}"
                ),
                value=(
                    "** **"
                    if not self.locked
                    else (
                        "*(Request an unlock\n"
                        "by clicking below.)*"
                    )
                ),
                inline=True
            ),
        ]

        if len(self.images) > 1:
            fields.append(
                EmbedField(
                    name=f"{BotEmojis.Camera} __Additional Images__",
                    value="\n".join([i.url for i in self.images[1:]]),
                    inline=False
                ),
            )

        if self._end_dt is not None and self._end_dt.tzinfo is None:
            self._end_dt = self.py_tz.localize(self._end_dt)

        return U.make_embed(
            title=f"__{self.name}__" if self.name else f"__Room #{self.index:03d}__",
            description=f"```{self.description}```" if self.description else None,
            fields=fields,
            footer_text=(
                (
                    "This room is currently IN USE.\n"
                    f"Occupant: {self._occupant.display_name}\n"
                    f"End Time: {self._end_dt.strftime('%H:%M')}"
                )
                if self._in_use
                else None
            ),
            image_url=self.images[0].url if self.images else None
        )

################################################################################
    def field(self) -> EmbedField:

        def emoji(attr: bool) -> PartialEmoji:
            return BotEmojis.CheckGreen if attr else BotEmojis.Cross

        return EmbedField(
            name=self.name or (f"Room #{self.index:03d}" if self.index else "`Unnumbered Room`"),
            value=(
                f"Theme: {self.theme or '`Not Set`'}\n"
                f"Locked: {emoji(self.locked)}\n"
                f"Disabled: {emoji(self.disabled)}\n"
            ),
            inline=True
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return RoomStatusView(user, self)

################################################################################
    async def set_index(self, interaction: Interaction) -> None:

        await self._details.set_index(interaction)

################################################################################
    async def set_name(self, interaction: Interaction) -> None:

        await self._details.set_name(interaction)

################################################################################
    async def set_owner(self, interaction: Interaction) -> None:

        await self._details.set_owner(interaction)

################################################################################
    async def set_theme(self, interaction: Interaction) -> None:

        await self._details.set_theme(interaction)

################################################################################
    async def set_description(self, interaction: Interaction) -> None:

        await self._details.set_description(interaction)

################################################################################
    async def toggle_locked(self, interaction: Interaction) -> None:

        await self._details.toggle_locked(interaction)

################################################################################
    async def set_emoji(self, interaction: Interaction) -> None:

        await self._details.set_emoji(interaction)

################################################################################
    async def toggle_disabled(self, interaction: Interaction) -> None:

        await self._details.toggle_disabled(interaction)

################################################################################
    def select_option(self) -> SelectOption:

        return SelectOption(
            label=self.name or (f"Room #{self.index:03d}" if self.index else "Unnumbered Room"),
            value=str(self.id)
        )

################################################################################
    async def add_image(self, interaction: Interaction) -> None:

        if len(self.images) > self.MAX_IMAGES:
            error = MaxItemsReached("Room Image", self.MAX_IMAGES)
            await interaction.respond(embed=error, ephemeral=True)
            return

        prompt = U.make_embed(
            title="__Add Room Image__",
            description=(
                "Please upload the image you would like to add to this room."
            )
        )
        image_url = await U.wait_for_image(interaction, prompt)
        if image_url is None:
            return

        new_image = RoomImage.new(self, image_url)
        self._images.append(new_image)

        confirm = U.make_embed(
            title="__Room Image Added__",
            description=(
                "The image has been successfully added to this room."
            )
        )
        await interaction.respond(embed=confirm, ephemeral=True)

################################################################################
    def get_image(self, image_id: int) -> Optional[RoomImage]:

        return next((i for i in self.images if i.id == int(image_id)), None)

################################################################################
    async def remove_image(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Select Image to Remove__",
            description=(
                "Please select the image you would like to remove from this room."
            )
        )
        view = FroggeSelectView(interaction.user, [i.select_option() for i in self.images])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        image = self.get_image(view.value)
        await image.remove(interaction)

################################################################################
    async def post(self, interaction: Interaction) -> None:

        post_channel = await self._mgr.channel  # type: ignore
        assert post_channel is not None, "Post channel is not set."

        if await self.update_post_components():
            return

        view = RoomReservationView(self)
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

################################################################################
    async def update_post_components(self) -> bool:

        if self._post_msg.id is None:
            return False

        view = RoomReservationView(self)
        self.bot.add_view(view)

        post_message = await self.post_message
        if post_message is None:
            return False

        try:
            await post_message.edit(embed=await self.compile(), view=view)
        except NotFound:
            self.post_message = None
            return False
        else:
            return True

################################################################################
    async def reserve(self, interaction: Interaction) -> None:

        options = [SelectOption(label=f"{x} Hours", value=str(x)) for x in range(1, 10)]
        prompt = U.make_embed(
            title="__Room Reservation__",
            description=(
                "Please select the duration you would like to reserve this room for."
            )
        )
        view = FroggeSelectView(interaction.user, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self._in_use = True
        self._occupant = interaction.user
        self._end_dt = self.py_tz.localize(datetime.now() + timedelta(hours=int(view.value)))

        await self.update_post_components()

################################################################################
    async def notify_owner(self, interaction: Interaction) -> None:

        owner = await self.owner
        if owner is None:
            return

        prompt = U.make_embed(
            title="__Room Reservation__",
            description=(
                f"{interaction.user.mention} would like you to unlock your room.\n\n"
                
                "Please contact them immediately to discuss this request."
            )
        )

        try:
            await owner.send(embed=prompt)
        except Forbidden:
            embed = U.make_error(
                title="Unable to Notify Owner",
                message="I was unable to send a message to the owner of this room.",
                solution="Please ensure they have their DMs enabled."
            )
        except NotFound:
            embed = U.make_error(
                title="Unable to Notify Owner",
                message="I was unable to send a message to the owner of this room.",
                solution="Please ensure they are still a member of the server."
            )
        else:
            embed = U.make_embed(
                title="__Owner Notified__",
                description=(
                    "The owner of this room has been notified of your request."
                )
            )

        await interaction.respond(embed=embed, ephemeral=True)

################################################################################
    def _reset_in_use(self) -> None:

        self._in_use = False
        self._occupant = None
        self._end_dt = None

################################################################################
    async def check_end_time(self) -> None:

        if self._end_dt is None:
            return

        def localize_if_needed(dt: datetime) -> datetime:
            return dt if dt.tzinfo is not None else self.py_tz.localize(dt)

        if localize_if_needed(datetime.now()) >= localize_if_needed(self._end_dt):
            self._reset_in_use()
            await self.update_post_components()

################################################################################
