from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional, Any, Dict, Type, TypeVar

from discord import Interaction, Embed, EmbedField, TextChannel, ChannelType
from dotenv import load_dotenv

from Enums import Timezone
from UI.Common import FroggeSelectView, BasicTextModal
from UI.Core import GuildConfigurationStatusView
from Utilities import Utilities as U
from logger import log

from Classes.Common import FroggeObject, LazyChannel

if TYPE_CHECKING:
    from Classes import GuildData
################################################################################
    
__all__ = ("GuildConfiguration",)

GC = TypeVar("GC", bound="GuildConfiguration")

################################################################################
class GuildConfiguration(FroggeObject):

    __slots__ = (
        "_parent",
        "_tz",
        "_log_channel",
    )

    RESTRICTED_SERVERS = [
        992483766306078840,  # FROG
    ]
    
################################################################################
    def __init__(self, parent: GuildData):
        
        self._parent: GuildData = parent
        
        self._tz: Timezone = Timezone(7)  # Default to EST
        self._log_channel: LazyChannel = LazyChannel(self, None)
        
################################################################################
    async def load(self,  data: Dict[str, Any]) -> None:

        self._tz = Timezone(data["timezone"])
        self._log_channel = LazyChannel(self, data["log_channel_id"])
        
################################################################################
    def to_dict(self) -> Dict[str, Any]:
        
        return {
            "timezone": self._tz.value,
            "log_channel_id": self._log_channel._item_id
        }
    
################################################################################
    @property
    def guild(self) -> GuildData:
        
        return self._parent
    
################################################################################
    @property
    def timezone(self) -> Timezone:
        
        return self._tz
    
    @timezone.setter
    def timezone(self, value: Timezone) -> None:
        
        self._tz = value
        self.update()
    
################################################################################
    @property
    async def log_channel(self) -> Optional[TextChannel]:
        
        return await self._log_channel.get()
    
    @log_channel.setter
    def log_channel(self, value: Optional[TextChannel]) -> None:
        
        self._log_channel.set(value)
        
################################################################################
    def update(self) -> None:
        
        self._parent.bot.api.update_guild_configuration(
            self._parent.guild_id, 
            **self.to_dict()
        )
        
################################################################################
    async def status(self) -> Embed:
        
        log_channel = await self.log_channel
        return U.make_embed(
            title="__General Server Configuration__",
            fields=[
                EmbedField(
                    name="__Log Channel__", 
                    value=(
                        log_channel.mention
                        if log_channel is not None
                        else "`Not Set`"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__Operating Timezone__",
                    value=f"`{self.timezone.proper_name}`",
                    inline=True
                )
            ]
        )
    
################################################################################
    async def main_menu(self, interaction: Interaction) -> None:

        # Prompt for password if on a restricted server (FROG)
        if interaction.guild_id in self.RESTRICTED_SERVERS:
            load_dotenv()
            if os.getenv("DEBUG") != "True":
                modal = BasicTextModal(
                    title="Password Required",
                    attribute="Password",
                    max_length=10,
                    example="Enter the password to access this menu."
                )

                await interaction.response.send_modal(modal)
                await modal.wait()

                if not modal.complete or modal.value is False:
                    return

                if modal.value != os.getenv("ADMIN_PASSWORD"):
                    await interaction.respond("Incorrect password. Please try again.", ephemeral=True)
                    return

        embed = await self.status()
        view = GuildConfigurationStatusView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
        
################################################################################
    async def set_log_channel(self, interaction: Interaction) -> None:

        log.info(self._parent, f"Setting Channel: Log Stream")

        prompt = U.make_embed(
            title=f"Set `Log Stream` Channel",
            description=(
                f"Please enter a mention for the channel you would like to set/add as "
                f"the `Log Stream` channel."
            )
        )

        channel = await U.listen_for(
            interaction, prompt, U.MentionableType.Channel, [ChannelType.text]
        )
        if channel is None:
            return

        self.log_channel = channel
        log.debug(self._parent, f"Channel: {channel.name} ({channel.id})")
        
################################################################################
    async def set_timezone(self, interaction: Interaction) -> None:
        
        log.info(self._parent, "Setting timezone...")

        prompt = U.make_embed(
            title="Timezone Selection",
            description=(
                "Please select your timezone from the list below..."
            )
        )
        view = FroggeSelectView(
            owner=interaction.user,
            options=Timezone.select_options(),
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        tz = Timezone(int(view.value))
        
        if tz is not None:
            self.timezone = tz
            log.info(self._parent, f"Timezone set to {tz.proper_name}.")
        else:
            log.info(self._parent, "Timezone not set.")
    
################################################################################
    async def configure_verification(self, interaction: Interaction) -> None:

        await self._parent.verification_manager.main_menu(interaction)

################################################################################
        
        