from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, Type, Any, Dict, Optional, Tuple, List

from discord import (
    Interaction,
    Embed,
    User,
    Colour,
    EmbedField,
    TextChannel,
    Thread,
    SelectOption,
    Forbidden,
    NotFound,
    ChannelType,
    ForumChannel,
    Message
)

from Assets import BotEmojis, BotImages
from Classes.Common import ManagedObject, LazyMessage, LazyUser
from Errors import ProfileIncomplete, ChannelMissing, InsufficientPermissions
from .ProfileDetails import ProfileDetails
from .ProfileAtAGlance import ProfileAtAGlance
from .ProfilePersonality import ProfilePersonality
from .ProfileImages import ProfileImages
from Utilities import Utilities as U
from UI.Profiles import ProfileMainMenuView
from UI.Common import CloseMessageView, FroggeSelectView
from Utilities.Constants import MAX_EMBED_LENGTH

if TYPE_CHECKING:
    from Classes import ProfileManager
    from UI.Common import FroggeView
################################################################################

__all__ = ("Profile", )

P = TypeVar("P", bound="Profile")

################################################################################
class Profile(ManagedObject):

    __slots__ = (
        "_user",
        "_details",
        "_aag",
        "_personality",
        "_images",
        "_post_msg",
    )
    
################################################################################
    def __init__(self, mgr: ProfileManager, user_id: int, _id: int, **kwargs) -> None:

        super().__init__(mgr, _id)
        
        self._user: LazyUser = LazyUser(self, user_id)
        
        self._details: ProfileDetails = ProfileDetails(self)
        self._aag: ProfileAtAGlance = ProfileAtAGlance(self)
        self._personality: ProfilePersonality = ProfilePersonality(self)
        self._images: ProfileImages = ProfileImages(self)
        
        self._post_msg: LazyMessage = LazyMessage(self, kwargs.get("post_url"))
    
################################################################################
    @classmethod
    def new(cls: Type[P], mgr: ProfileManager, user_id: int, **kwargs) -> P:
        
        new_profile = mgr.bot.api.create_profile(mgr.guild_id, user_id)
        return cls(mgr, user_id, new_profile["id"])
    
################################################################################
    @classmethod
    def load(cls: Type[P], mgr: ProfileManager, data: Dict[str, Any]) -> P:
        
        self: P = cls.__new__(cls)
        
        self._id = data["id"]
        self._mgr = mgr
        self._user = LazyUser(self, data["user_id"])
        
        self._details = ProfileDetails.load(self, data["details"])
        self._aag = ProfileAtAGlance.load(self, data["ataglance"])
        self._personality = ProfilePersonality.load(self, data["personality"])
        self._images = ProfileImages.load(self, data["images"])
        
        self._post_msg = LazyMessage(self, data["post_url"])
        
        return self
    
################################################################################
    def __len__(self) -> int:

        return len(self.compile()[0])

################################################################################
    def is_complete(self) -> bool:

        return self._mgr.requirements.check(self)  # type: ignore

################################################################################
    @property
    def name(self) -> Optional[str]:
        
        return self._details.name
    
################################################################################
    @property
    def color(self) -> Optional[Colour]:
        
        return self._details.color
    
################################################################################
    @property
    async def post_message(self) -> Optional[Message]:
        
        return await self._post_msg.get()
    
    @post_message.setter
    def post_message(self, value: Message) -> None:
        
        self._post_msg.set(value)
        
################################################################################
    def update(self) -> None:
        
        self.bot.api.update_profile(self)
    
################################################################################
    def to_dict(self) -> Dict[str, Any]:
        
        return {
            "post_url": self._post_msg.id
        }
    
################################################################################
    async def status(self) -> Embed:

        return U.make_embed(
            title=f"__Profile Menu for `{self.name}`__",
            description=(
                "Select a button below to view or edit the corresponding "
                "section of your profile!"
            )
        )

################################################################################
    def compile(self) -> Tuple[Embed, Optional[Embed]]:

        char_name, url, color, jobs, rates_field = self._details.compile()
        ataglance = self._aag.compile()
        likes, dislikes, personality, aboutme = self._personality.compile()
        thumbnail, main_image, additional_imgs = self._images.compile()

        if char_name is None:
            char_name = f"Character Name: `Not Set`"
        elif url is not None:
            char_name = f"{BotEmojis.Envelope}  {char_name}  {BotEmojis.Envelope}"

        fields: List[EmbedField] = []
        if ataglance is not None:
            fields.append(ataglance)
        if rates_field is not None:
            fields.append(rates_field)
        if likes is not None:
            fields.append(likes)
        if dislikes is not None:
            fields.append(dislikes)
        if personality is not None:
            fields.append(personality)
        if additional_imgs is not None:
            additional_imgs.value += U.draw_line(extra=15)
            fields.append(additional_imgs)

        main_profile = U.make_embed(
            color=color or Colour.embed_background(),
            title=char_name,
            # description=description,
            url=url,
            thumbnail_url=thumbnail,
            image_url=main_image,
            fields=fields
        )

        return main_profile, aboutme
    
################################################################################
    def get_menu_view(self, user: User) -> FroggeView:
        
        return ProfileMainMenuView(user, self)

################################################################################
    async def main_details_menu(self, interaction: Interaction) -> None:

        await self._details.menu(interaction)

################################################################################
    async def ataglance_menu(self, interaction: Interaction) -> None:

        await self._aag.menu(interaction)

################################################################################
    async def personality_menu(self, interaction: Interaction) -> None:

        await self._personality.menu(interaction)
        
################################################################################
    async def images_menu(self, interaction: Interaction) -> None:

        await self._images.menu(interaction)

################################################################################
    async def preview_profile(self, interaction: Interaction) -> None:

        main_profile, _ = self.compile()
        view = CloseMessageView(interaction.user)

        await interaction.respond(embed=main_profile, view=view)
        await view.wait()

################################################################################
    async def preview_aboutme(self, interaction: Interaction) -> None:

        _, aboutme = self.compile()
        if aboutme is None:
            error = U.make_error(
                title="About Me Not Set",
                message="You can't view an empty About Me section.",
                solution=(
                    "Fill it out in the `Profile Personality` section before "
                    "trying again."
                )
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        view = CloseMessageView(interaction.user)

        await interaction.respond(embed=aboutme, view=view)
        await view.wait()

################################################################################
    async def post(self, interaction: Interaction) -> None:

        error = None
        if not await self._mgr.allowed_to_post(interaction.user):  # type: ignore
            error = U.make_error(
                title="Profile Role Not Owned",
                message="You don't own at least one of the roles required to use this command.",
                solution=(
                    "Please contact a server administrator to have them assign "
                    "you the appropriate role(s)."
                )
            )
        if not self._mgr.channel_groups:  # type: ignore
            error = U.make_error(
                title="Profile Posting Channel Not Set",
                message="The profile posting channel(s) have not been set for this server.",
                solution=(
                    "Please contact a server administrator to set the "
                    "profile posting channel(s)."
                )
            )
        if len(self) > MAX_EMBED_LENGTH:
            error = U.make_error(
                title="Profile Too Large!",
                description=f"Current Character Count: `{len(self):,}`.",
                message=(
                    f"Your profile is larger than Discord's mandatory {MAX_EMBED_LENGTH:,}"
                    f"-character limit for embedded messages."
                ),
                solution=(
                    "The total number of characters in all your profile's sections "
                    f"must not exceed {MAX_EMBED_LENGTH:,}."
                )
            )
        if not self.is_complete():
            error = ProfileIncomplete(self, self._mgr.requirements.active_requirements)  # type: ignore

        if error is not None:
            await interaction.respond(embed=error, ephemeral=True)
            return

        if await self.update_post_components():
            await interaction.respond(embed=self.success_message())
            return

        options = [
            SelectOption(
              label=channel.name,
              value=str(channel.id),
            )
            for channel 
            in await self._mgr.post_channels_for(interaction.user)  # type: ignore
        ][:25]

        if not options:
            error = U.make_error(
                title="Profile Posting Channel Not Set",
                message="The profile posting channel(s) have not been set for your role.",
                solution=(
                    "Please contact a server administrator to set the "
                    "profile posting channel(s)."
                )
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        if len(options) > 1:
            prompt = U.make_embed(
                title="__Select Profile Posting Channel__",
                description=(
                    "Select the channel you would like to post your profile in!\n"
                    "Please note that you can only post in one channel at a time."
                )
            )
            view = FroggeSelectView(
                owner=interaction.user,
                options=options
            )
        
            await interaction.respond(embed=prompt, view=view)
            await view.wait()
        
            if not view.complete or view.value is False:
                return
        
            channel: Union[TextChannel, ForumChannel] = (  # type: ignore
                await self._mgr.guild.get_or_fetch_channel(int(view.value))
            )
        else:
            channel = await self._mgr.guild.get_or_fetch_channel(options[0].value)  # type: ignore
        
        if channel is None:
            error = ChannelMissing()
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        post_embeds = [e for e in self.compile() if e is not None]
        if channel.type == ChannelType.text:
            post_msg = await channel.send(embeds=post_embeds)  # type: ignore
            self._post_msg.set(post_msg)
            self.update()
            await interaction.respond(embed=self.success_message())
            return
        
        # Must be a forum channel
        matching_thread = next(
            (t for t in channel.threads if t.name.lower() == self.name.lower()),  # type: ignore
            None
        )
        if matching_thread:
            async for m in matching_thread.history():
                await m.delete()
            action = matching_thread.send  # type: ignore
        else:
            action = lambda **kw: channel.create_thread(name=self.name, **kw)  # type: ignore
        
        try:
            result = await action(embeds=post_embeds)
            if isinstance(result, Thread):
                post_msg = await result.fetch_message(result.last_message_id)
            else:
                post_msg = result
            self._post_msg.set(post_msg)
            self.update()
            await interaction.respond(embed=self.success_message())
        except Forbidden:
            error = InsufficientPermissions(channel, "Send Messages")
            await interaction.respond(embed=error, ephemeral=True)

################################################################################
    async def update_post_components(self) -> bool:

        post_message = await self.post_message
        if post_message is None:
            return False

        try:
            await post_message.edit(embeds=[e for e in self.compile() if e is not None])
        except NotFound:
            self.post_message = None
            return False
        else:
            return True

################################################################################
    def success_message(self) -> Embed:

        return U.make_embed(
            color=Colour.brand_green(),
            title="Profile Posted!",
            description=(
                "Hey, good job, you did it! Your profile was posted successfully!\n"
                f"{U.draw_line(extra=37)}\n"
                f"(__Character Name:__ ***{self.name}***)\n\n"

                f"{BotEmojis.ArrowRight}  [Check It Out HERE!]"
                f"({self._post_msg.id})  {BotEmojis.ArrowLeft}\n"
                f"{U.draw_line(extra=16)}"
            ),
            thumbnail_url=BotImages.ThumbsUpFrog,
            timestamp=True
        )

################################################################################
    async def progress(self , interaction: Interaction) -> None:

        em_final = self._details.progress_emoji(self._post_msg.id)
        progress = U.make_embed(
            color=self.color,
            title="Profile Progress",
            description=(
                self._details.progress() +
                self._aag.progress() +
                self._personality.progress() +
                self._images.progress() +
                f"{U.draw_line(extra=15)}\n"
                f"{em_final} -- Finalize"
            ),
            timestamp=False
        )
        view = CloseMessageView(interaction.user)

        await interaction.response.send_message(embed=progress, view=view)
        await view.wait()

################################################################################
    async def delete_post(self) -> None:

        if self._post_msg.id is None:
            return

        post_msg = await self.post_message
        if post_msg is None:
            return

        try:
            await post_msg.delete()
            self.post_message = None
        except NotFound:
            pass

################################################################################
