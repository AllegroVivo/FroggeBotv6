from __future__ import annotations

from typing import TYPE_CHECKING, Optional, TypeVar, Type, Any, Dict
from Enums import VIPMessageType
from discord import Embed, Interaction
from UI.VIPs import VIPMessageStatusView
from Utilities import Utilities as U
from UI.Common import BasicTextModal

if TYPE_CHECKING:
    from Classes import VIPManager, FroggeBot, GuildData
################################################################################

__all__ = ("VIPMessage", )

VM = TypeVar("VM", bound="VIPMessage")

################################################################################
class VIPMessage:

    __slots__ = (
        "_mgr",
        "_type",
        "_title",
        "_description",
        "_thumbnail",
        "_active",
    )
    
################################################################################
    def __init__(self, mgr: VIPManager, _type: VIPMessageType, **kwargs) -> None:

        self._mgr: VIPManager = mgr
        self._type: VIPMessageType = _type
        
        self._title: Optional[str] = kwargs.get("title")
        self._description: Optional[str] = kwargs.get("description")
        self._thumbnail: Optional[str] = kwargs.get("thumbnail")
        self._active: bool = kwargs.get("active", True)
    
################################################################################
    @classmethod
    def load(cls: Type[VM], mgr: VIPManager, data: Dict[str, Any]) -> VM:
        
        self: VM = cls.__new__(cls)
        
        self._mgr = mgr
        self._type = VIPMessageType(data["message_type"])
        self._title = data.get("title")
        self._description = data.get("description")
        self._thumbnail = data.get("thumbnail")
        self._active = data.get("active", True)
        
        return self
    
################################################################################
    @property
    def bot(self) -> FroggeBot:
        
        return self._mgr.bot
    
################################################################################
    @property
    def guild(self) -> GuildData:
    
        return self._mgr.guild
    
################################################################################
    @property
    def guild_id(self) -> int:
        
        return self.guild.guild_id
    
################################################################################
    @property
    def title(self) -> Optional[str]:
        
        return self._title
    
    @title.setter
    def title(self, value: Optional[str]) -> None:
        
        self._title = value
        self.update()
        
################################################################################
    @property
    def description(self) -> Optional[str]:
        
        return self._description
    
    @description.setter
    def description(self, value: Optional[str]) -> None:
        
        self._description = value
        self.update()
        
################################################################################
    @property
    def thumbnail(self) -> Optional[str]:
        
        return self._thumbnail
    
    @thumbnail.setter
    def thumbnail(self, value: Optional[str]) -> None:
        
        self._thumbnail = value
        self.update()
        
################################################################################
    @property
    def is_active(self) -> bool:
        
        return self._active
    
    @is_active.setter
    def is_active(self, value: bool) -> None:
        
        self._active = value
        self.update()
        
################################################################################
    def update(self) -> None:
        
        self.bot.api.update_vip_message(self)
        
################################################################################
    def to_dict(self) -> Dict[str, Any]:
        
        return {
            "guild_id": self.guild_id,
            "message_type": self._type.value,
            "title": self._title,
            "description": self._description,
            "thumbnail_url": self._thumbnail,
            "is_active": self._active,
        }
    
################################################################################
    def status(self) -> Embed:

        description = ""
        if self._type is VIPMessageType.Warning:
            description += (
                f"**Warning Threshold**: `{self._mgr.warning_threshold}x` days in advance\n"
            )

        description += (
            f"{U.draw_line(extra=25)}\n"
            f"**Title:**\n```{self._title}```\n"
            f"**Description:**\n```{self._description}```\n"
        )

        return U.make_embed(
            title=(
                "__VIP Warning Message Overview__"
                if self._type is VIPMessageType.Warning
                else "__VIP Expiry Message Overview__"
            ),
            description=description,
            thumbnail_url=self.thumbnail
        )
    
################################################################################
    async def main_menu(self, interaction: Interaction) -> None:

        embed = self.status()
        view = VIPMessageStatusView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def set_title(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Message Title",
            attribute="Title",
            cur_val=self.title,
            example="e.g. 'Your membership is about to expire!'",
            max_length=80,
            required=False,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.title = modal.value

################################################################################
    async def set_description(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Message Description",
            attribute="Description",
            cur_val=self.description,
            example=None,
            max_length=1000,
            required=False,
            multiline=True
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.description = modal.value

################################################################################
    async def set_thumbnail(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="VIP Warning Message Thumbnail",
            description=(
                "Please upload a thumbnail image to use for the VIP Warning Message."
            )
        )

        image = await U.wait_for_image(interaction, prompt)
        if image is not None:
            self.thumbnail = image

################################################################################
    async def set_warning_threshold(self, interaction: Interaction) -> None:

        await self._mgr.set_warning_threshold(interaction)

################################################################################
    async def toggle_active(self, interaction: Interaction) -> None:

        self.is_active = not self.is_active
        await interaction.respond("** **", delete_after=0.1)

################################################################################
