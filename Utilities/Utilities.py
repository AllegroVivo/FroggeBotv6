from __future__ import annotations

import math
import re
from datetime import datetime, time
from enum import Enum
from typing import Any, List, Optional, Tuple, Union, Literal, TYPE_CHECKING

import emoji
import pytz
from discord import (
    Colour,
    Embed,
    EmbedField,
    EmbedFooter,
    Interaction,
    NotFound,
    ChannelType,
    User,
    Role,
    Emoji, SelectOption, TextChannel, ForumChannel, Message
)
from discord.abc import GuildChannel

from Enums import Timezone
from UI.Common import FroggeSelectView
from UI.Common.FroggeMultiMenuSelect import FroggeMultiMenuSelect
from .Colors import CustomColor
from .ErrorMessage import ErrorMessage

if TYPE_CHECKING:
    from Classes import GuildData
################################################################################

__all__ = ("Utilities", )

TimestampStyle = Literal["f", "F", "d", "D", "t", "T", "R"]

################################################################################
class Utilities:
    """A collection of utility functions for use in various parts of the bot."""

    TIMEZONE_OFFSETS = {
        Timezone.MIT: pytz.timezone('Pacific/Midway'),
        Timezone.HST: pytz.timezone('Pacific/Honolulu'),
        Timezone.AST: pytz.timezone('US/Alaska'),
        Timezone.PST: pytz.timezone('US/Pacific'),
        Timezone.MST: pytz.timezone('US/Mountain'),
        Timezone.CST: pytz.timezone('US/Central'),
        Timezone.EST: pytz.timezone('US/Eastern'),
        Timezone.PRT: pytz.timezone('America/Puerto_Rico'),
        Timezone.AGT: pytz.timezone('America/Argentina/Buenos_Aires'),
        Timezone.CAT: pytz.timezone('Africa/Harare'),
        Timezone.UTC: pytz.timezone('UTC'),
        Timezone.ECT: pytz.timezone('Europe/Paris'),
        Timezone.EET: pytz.timezone('Europe/Bucharest'),
        Timezone.EAT: pytz.timezone('Africa/Nairobi'),
        Timezone.NET: pytz.timezone('Asia/Yerevan'),
        Timezone.PLT: pytz.timezone('Asia/Karachi'),
        Timezone.BST: pytz.timezone('Asia/Dhaka'),
        Timezone.VST: pytz.timezone('Asia/Ho_Chi_Minh'),
        Timezone.CTT: pytz.timezone('Asia/Shanghai'),
        Timezone.JST: pytz.timezone('Asia/Tokyo'),
        Timezone.AET: pytz.timezone('Australia/Sydney'),
        Timezone.SST: pytz.timezone('Pacific/Guadalcanal'),
        Timezone.NST: pytz.timezone('Pacific/Auckland'),
    }
    
################################################################################
    @staticmethod
    def ensure_timezone(dt: datetime, tz: Timezone) -> datetime:

        return dt if dt.tzinfo else Utilities.TIMEZONE_OFFSETS[tz].localize(dt)

################################################################################
    @staticmethod
    def make_embed(
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        url: Optional[str] = None,
        color: Optional[Union[Colour, int]] = None,
        thumbnail_url: Optional[str] = None,
        image_url: Optional[str] = None,
        author_text: Optional[str] = None,
        author_url: Optional[str] = None,
        author_icon: Optional[str] = None,
        footer_text: Optional[str] = None,
        footer_icon: Optional[str] = None,
        timestamp: Union[datetime, bool] = False,
        fields: Optional[List[Union[Tuple[str, Any, bool], EmbedField]]] = None,
        _color_override: bool = False
    ) -> Embed:
        """Creates and returns a Discord embed with the provided parameters.
    
        All parameters are optional.
    
        Parameters:
        -----------
        title: :class:`str`
            The embed's title.
    
        description: :class:`str`
            The main text body of the embed.
    
        url: :class:`str`
            The URL for the embed title to link to.
    
        color: Optional[Union[:class:`Colour`, :class:`int`]]
            The desired accent color. Defaults to :func:`colors.random_all()`
    
        thumbnail_url: :class:`str`
            The URL for the embed's desired thumbnail image.
    
        image_url: :class:`str`
            The URL for the embed's desired main image.
    
        footer_text: :class:`str`
            The text to display at the bottom of the embed.
    
        footer_icon: :class:`str`
            The icon to display to the left of the footer text.
    
        author_name: :class:`str`
            The text to display at the top of the embed.
    
        author_url: :class:`str`
            The URL for the author text to link to.
    
        author_icon: :class:`str`
            The icon that appears to the left of the author text.
    
        timestamp: Union[:class:`datetime`, `bool`]
            Whether to add the current time to the bottom of the embed.
            Defaults to ``False``.
    
        fields: Optional[List[Union[Tuple[:class:`str`, Any, :class:`bool`], :class:`EmbedField`]]]
            List of tuples or EmbedFields, each denoting a field to be added
            to the embed. If entry is a tuple, values are as follows:
                0 -> Name | 1 -> Value | 2 -> Inline (bool)
            Note that in the event of a tuple, the value at index one is automatically cast to a string for you.
    
        Returns:
        --------
        :class:`Embed`
            The finished embed object.
        """

        if title:
            if not title.startswith("__") and not title.endswith("__"):
                title = f"__{title}__"

        embed = Embed(
            colour=(
                color
                if color is not None
                else CustomColor.random_all()
            ) if not _color_override else color,
            title=title,
            description=description,
            url=url
        )

        embed.set_thumbnail(url=thumbnail_url)
        embed.set_image(url=image_url)

        if author_text is not None:
            embed.set_author(
                name=author_text,
                url=author_url,
                icon_url=author_icon
            )

        if footer_text is not None:
            embed.set_footer(
                text=footer_text,
                icon_url=footer_icon
            )

        if isinstance(timestamp, datetime):
            embed.timestamp = timestamp
        elif timestamp is True:
            embed.timestamp = datetime.now()

        if fields is not None:
            if all(isinstance(f, EmbedField) for f in fields):
                embed.fields = fields
            else:
                for f in fields:
                    if isinstance(f, EmbedField):
                        embed.fields.append(f)
                    elif isinstance(f, tuple):
                        embed.add_field(name=f[0], value=f[1], inline=f[2])
                    else:
                        continue

        return embed

################################################################################
    @staticmethod
    def make_error(
        *,
        title: str,
        message: str,
        solution: str,
        description: Optional[str] = None
    ) -> Embed:

        # We only need this function as a basic wrapper, so we don't need to
        # subclass ErrorMessage every single time. v5 edit. ~SP 8/19/24
        return ErrorMessage(
            title=title,
            message=message,
            solution=solution,
            description=description
        )
    
################################################################################
    @staticmethod
    def _text_length(text: str) -> float:

        value = 0.0

        for c in text:
            if c == "'":
                value += 0.25
            elif c in ("i", "j", ".", " "):
                value += 0.30
            elif c in ("I", "!", ";", "|", ","):
                value += 0.35
            elif c in ("f", "l", "`", "[", "]"):
                value += 0.40
            elif c in ("(", ")", "t"):
                value += 0.45
            elif c in ("r", "t", "1" "{", "}", '"', "\\", "/"):
                value += 0.50
            elif c in ("s", "z", "*", "-"):
                value += 0.60
            elif c in ("x", "^"):
                value += 0.65
            elif c in ("a", "c", "e", "g", "k", "v", "y", "J", "7", "_", "=", "+", "~", "<", ">", "?"):
                value += 0.70
            elif c in ("n", "o", "u", "2", "5", "6", "8", "9"):
                value += 0.75
            elif c in ("b", "d", "h", "p", "q", "E", "F", "L", "S", "T", "Z", "3", "4", "$"):
                value += 0.80
            elif c in ("P", "V", "X", "Y", "0"):
                value += 0.85
            elif c in ("A", "B", "C", "D", "K", "R", "#", "&"):
                value += 0.90
            elif c in ("G", "H", "U"):
                value += 0.95
            elif c in ("w", "N", "O", "Q", "%"):
                value += 1.0
            elif c in ("m", "W"):
                value += 1.15
            elif c == "M":
                value += 1.2
            elif c == "@":
                value += 1.3

        return value

################################################################################
    @staticmethod
    def draw_line(*, text: str = "", num_emoji: int = 0, extra: float = 0.0) -> str:

        text_value = extra + (1.95 * num_emoji) + Utilities._text_length(text)
        return "═" * math.ceil(text_value)

################################################################################
    @staticmethod
    def format_dt(dt: datetime, /, style: TimestampStyle | None = None) -> str:
        """(Copied from Py-Cord)
        A helper function to format a :class:`datetime.datetime` for presentation within Discord.

        This allows for a locale-independent way of presenting data using Discord specific Markdown.

        +-------------+----------------------------+-----------------+
        |    Style    |       Example Output       |   Description   |
        +=============+============================+=================+
        | t           | 22:57                      | Short Time      |
        +-------------+----------------------------+-----------------+
        | T           | 22:57:58                   | Long Time       |
        +-------------+----------------------------+-----------------+
        | d           | 17/05/2016                 | Short Date      |
        +-------------+----------------------------+-----------------+
        | D           | 17 May 2016                | Long Date       |
        +-------------+----------------------------+-----------------+
        | f (default) | 17 May 2016 22:57          | Short Date Time |
        +-------------+----------------------------+-----------------+
        | F           | Tuesday, 17 May 2016 22:57 | Long Date Time  |
        +-------------+----------------------------+-----------------+
        | R           | 5 years ago                | Relative Time   |
        +-------------+----------------------------+-----------------+

        Note that the exact output depends on the user's locale setting in the client. 
        The example output presented is using the ``en-GB`` locale.

        Parameters
        ----------
        dt: :class:`datetime.datetime`
            The datetime to format.
        style: :class:`str`
            The style to format the datetime with.

        Returns
        -------
        :class:`str`
            The formatted string.
        """
        if style is None:
            return f"<t:{int(dt.timestamp())}>"
        return f"<t:{int(dt.timestamp())}:{style}>"

################################################################################
    @staticmethod
    def time_to_datetime(_time: time) -> datetime:

        return datetime(
            year=2069,
            month=4,
            day=20,
            hour=_time.hour,
            minute=_time.minute,
            second=_time.second,
        )

################################################################################
    @staticmethod
    def titleize(text: str) -> str:
    
        return re.sub(
            r"[A-Za-z]+('[A-Za-z]+)?",
            lambda word: word.group(0).capitalize(),
            text
        )   

################################################################################
    @staticmethod
    def parse_salary(salary: str) -> Optional[int]:
    
        # Remove commas and whitespace, and make lowercase
        salary = salary.lower().strip().replace(",", "")
    
        try:
            if salary.endswith("k"):
                ret = int(float(salary[:-1]) * 1000)
            elif salary.endswith("m"):
                ret = int(float(salary[:-1]) * 1000000)
            else:
                ret = int(float(salary))
        except ValueError:
            return
        else:
            return min(max(ret, 0), 999999999)

################################################################################
    @staticmethod
    def abbreviate_number(number: int) -> str:
        
        if number is None:
            return "N/A"
    
        if number < 1000:
            return str(number)
        elif number < 1000000:
            if number % 1000 == 0:
                return f"{number // 1000}k"
            else:
                return f"{number / 1000:.1f}k"
        else:
            if number % 1000000 == 0:
                return f"{number // 1000000}m"
            else:
                return f"{number / 1000000:.1f}m"
        
################################################################################
    @staticmethod
    def localize_dt(dt: datetime, timezone: Timezone) -> datetime:

        tz = Utilities.TIMEZONE_OFFSETS[timezone]
        return tz.localize(dt) if dt.tzinfo is None else dt.astimezone(tz)

################################################################################
    class MentionableType(Enum):
    
        Role = 0
        User = 1
        Channel = 2
        Emoji = 3
        
################################################################################
    @staticmethod
    async def listen_for(
        interaction: Interaction,
        prompt: Embed,
        mentionable_type: MentionableType,
        channel_restrictions: Optional[List[ChannelType]] = None
    ) -> Optional[Union[Role, User, GuildChannel, Emoji]]:

        if channel_restrictions and mentionable_type != Utilities.MentionableType.Channel:
            raise ValueError("Channel restriction can only be used with MentionableType.Channel")

        match mentionable_type:
            case Utilities.MentionableType.User:
                pattern = r"<@!?(\d+)>"
            case Utilities.MentionableType.Role:
                pattern = r"<@&(\d+)>"
            case Utilities.MentionableType.Channel:
                pattern = r"<#(\d+)>"
            case Utilities.MentionableType.Emoji:
                pattern = r"<a?:\w+:(\d+)>"
            case _:
                raise ValueError(f"Invalid MentionableType: {mentionable_type}")

        if not prompt.footer:
            prompt.footer = EmbedFooter(text="Type 'cancel' to stop the operation.")

        response = await interaction.respond(embed=prompt)

        def check(m):
            return (
                m.author == interaction.user
                and (x := re.match(pattern, m.content))
                or Utilities.is_unicode_emoji(m.content)
            ) or m.content.lower() == "cancel"

        try:
            message = await interaction.client.wait_for("message", check=check, timeout=180)
        except TimeoutError:
            embed = Utilities.make_embed(
                title="Timeout",
                description=(
                    "You took too long to respond. Please try again."
                ),
                color=CustomColor.brand_red()
            )
            await response.respond(embed=embed)
            return

        if mentionable_type is not Utilities.MentionableType.Emoji:
            error = Utilities.make_embed(
                title="Invalid Mention",
                description="You did not provide a valid mention. Please try again.",
                color=CustomColor.brand_red()
            )
        else:
            error = Utilities.make_embed(
                title="Invalid Emoji",
                description=(
                    "You did not provide a valid emoji. Please use a standard "
                    "unicode emoji or a custom emoji from within this server."
                ),
                color=CustomColor.brand_red()
            )

        if message.content.lower() == "cancel":
            embed = Utilities.make_embed(
                title="Cancelled",
                description="You have cancelled the operation.",
                color=CustomColor.brand_red()
            )
            await interaction.respond(embed=embed, ephemeral=True, delete_after=5)
            try:
                await message.delete()
                await response.delete_original_response()
            except NotFound:
                pass
            finally:
                return

        results = re.match(pattern, message.content)
        if not results and not Utilities.is_unicode_emoji(message.content):
            await interaction.respond(embed=error, ephemeral=True)
            try:
                await message.delete()
                await response.delete_original_response()
            except NotFound:
                pass
            finally:
                return

        if results:
            mentionable_id = int(results.group(1))
            guild: GuildData = interaction.client[interaction.guild_id]  # type: ignore

            match mentionable_type:
                case Utilities.MentionableType.User:
                    mentionable = await guild.get_or_fetch_member_or_user(mentionable_id)
                case Utilities.MentionableType.Channel:
                    mentionable = await guild.get_or_fetch_channel(mentionable_id)
                case Utilities.MentionableType.Role:
                    mentionable = await guild.get_or_fetch_role(mentionable_id)
                case Utilities.MentionableType.Emoji:
                    mentionable = await guild.get_or_fetch_emoji(mentionable_id)
                case _:
                    raise ValueError(f"Invalid MentionableType: {mentionable_type}")

            if not mentionable:
                await interaction.respond(embed=error, ephemeral=True)
                return
        else:
            mentionable = message.content

        try:
            await message.delete()
        except (NotFound, AttributeError):
            pass

        try:
            await response.delete_original_response()
        except AttributeError:
            try:
                await response.delete()
            except:
                pass
        except:
            pass

        if channel_restrictions and mentionable.type not in channel_restrictions:
            error = Utilities.make_embed(
                title="Invalid Channel",
                description=(
                    f"You must mention a valid channel of type "
                    f"`{'/'.join(p.name.title() for p in channel_restrictions)}`. "
                    f"Please try again."
                ),
                color=CustomColor.brand_red()
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        return mentionable
            
################################################################################
    @staticmethod
    async def _clean_up_messages(messages: List[Message]) -> None:

        for msg in messages:
            try:
                await msg.delete()
            except (NotFound, AttributeError):
                pass

################################################################################
    @staticmethod
    async def wait_for_image(interaction: Interaction, prompt: Embed) -> Optional[str]:

        if not prompt.footer:
            prompt.footer = EmbedFooter(text="Type 'cancel' to stop the operation.")
            
        msg = await interaction.respond(embed=prompt)
        
        def check(m):
            return (
                m.author == interaction.user and (
                    (
                        len(m.attachments) > 0
                        and m.attachments[0].content_type in (
                            "image/png", "image/jpeg", "image/gif", 
                            "image/webp", "image/jpg", "image/apng"
                        )
                    )
                    or m.content.lower() == "cancel"
                )
            )

        try:
            message = await interaction.client.wait_for("message", check=check, timeout=300)
        except TimeoutError:
            embed = Utilities.make_embed(
                title="Timeout",
                description=(
                    "You took too long to upload an image. Please try again."
                ),
                color=CustomColor.brand_red()
            )
            await interaction.respond(embed=embed)
            return

        image_url = None
        if message.content.lower() != "cancel":
            intermediate = await interaction.respond("Processing image... Please wait...")
            try:
                image_url = await interaction.client.dump_image(message.attachments[0])  # type: ignore
            except NotFound:
                pass

            try:
                await intermediate.delete()
            except NotFound:
                pass

        try:
            await message.delete()
        except NotFound:
            pass

        try:
            await msg.delete_original_response()
        except NotFound:
            pass
        
        return image_url
    
################################################################################
    @staticmethod
    async def select_channel(
        interaction: Interaction,
        guild: GuildData,
        channel_type: str,
        channel_prompt: Optional[Embed] = None
    ) -> Optional[Union[TextChannel, ForumChannel]]:

        options = [
            SelectOption(
                label=channel.name,
                value=str(channel.id),
            )
            for channel in guild.parent.channels
            if channel.type == ChannelType.category
        ]

        prompt = Utilities.make_embed(
            title="__Category Selection__",
            description=(
                "Please select the category of the channel you would like to use"
                f"for the `{channel_type}`."
            )
        )
        view = FroggeMultiMenuSelect(interaction.user, None, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        category_id = int(view.value)
        category = await guild.get_or_fetch_channel(category_id)

        if not category:
            error = Utilities.make_embed(
                title="__Invalid Category__",
                description="The category you selected is somehow invalid. Please try again."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        options = [
            SelectOption(
                label=channel.name,
                value=str(channel.id),
            )
            for channel in category.channels  # type: ignore
            if channel.type in (ChannelType.text, ChannelType.forum)
        ]

        prompt = channel_prompt or Utilities.make_embed(
            title=f"__{channel_type.title()} Selection__",
            description=(
                f"Please select the specific channel you'd like to use for the "
                f"`{channel_type.lower()}`."
            )
        )
        view = FroggeMultiMenuSelect(interaction.user, None, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        channel_id = int(view.value)
        return await guild.get_or_fetch_channel(channel_id)

################################################################################
    @staticmethod
    def string_clamp(text: str, length: int) -> str:

        return text[:length - 3] + "..." if len(text) > length else text

################################################################################
    @staticmethod
    def is_unicode_emoji(e: str) -> bool:
        
        return e in emoji.EMOJI_DATA

################################################################################
