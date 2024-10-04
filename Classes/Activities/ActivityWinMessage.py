from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from discord import Embed, Interaction

from UI.Common import BasicTextModal
from UI.Core import ActivityWinMessageStatusView
from Utilities import Utilities as U
from Utilities.Constants import *

if TYPE_CHECKING:
    from Classes import BaseActivity, FroggeBot
################################################################################

__all__ = ("ActivityWinMessage", )

################################################################################
class ActivityWinMessage(ABC):

    __slots__ = (
        "_parent",
        "_title",
        "_description",
        "_thumbnail",
    )
    
################################################################################
    def __init__(
        self,
        parent: BaseActivity, 
        title: Optional[str], 
        description: Optional[str],
        thumbnail: Optional[str],
    ) -> None:

        self._parent: BaseActivity = parent
        
        self._title: Optional[str] = title
        self._description: Optional[str] = description
        self._thumbnail: Optional[str] = thumbnail

################################################################################
    @property
    def bot(self) -> FroggeBot:
        
        return self._parent.bot
    
################################################################################
    @property
    def title(self) -> str:
    
        return self._title or DEFAULT_ACTIVITY_WIN_TITLE
    
    @title.setter
    def title(self, value: str) -> None:
    
        self._title = value
        self.update()
        
################################################################################
    @property
    def description(self) -> str:
    
        return self._description or DEFAULT_ACTIVITY_WIN_DESCRIPTION.format(
            self._parent.activity_name.lower(), self._parent.name, self._parent.prize
        )
    
    @description.setter
    def description(self, value: str) -> None:
    
        self._description = value
        self.update()
        
################################################################################
    @property
    def thumbnail(self) -> str:
    
        return self._thumbnail or DEFAULT_ACTIVITY_WIN_THUMBNAIL
    
    @thumbnail.setter
    def thumbnail(self, value: str) -> None:
    
        self._thumbnail = value
        self.update()
        
################################################################################
    @abstractmethod
    def update(self) -> None:
        
        raise NotImplementedError
        
################################################################################
    def status(self) -> Embed:
        
        return U.make_embed(
            title=f"__{self._parent.activity_name} Win Message Management__",
            description=(
                f"**Title:**\n```{self.title}```\n"
                f"**Description:**\n```{self.description}```\n"
            ),
            thumbnail_url=self.thumbnail,
        )
        
################################################################################
    async def menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = ActivityWinMessageStatusView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
    
################################################################################
    async def set_title(self, interaction: Interaction) -> None:
        
        modal = BasicTextModal(
            title=f"Set {self._parent.activity_name} Win Message Title",
            attribute="Title",
            cur_val=self._title,
            example="eg. 'You Won!'",
            max_length=80
        )
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        self.title = modal.value
    
################################################################################
    async def set_description(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title=f"Set {self._parent.activity_name} Win Message Body Text",
            attribute="Body Text",
            cur_val=self._description,
            example="eg. 'Contact a host to claim your prize!'",
            max_length=500,
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
            title=f"Set {self._parent.activity_name} Win Message Thumbnail",
            description=(
                "Please upload the image you would like to use as the thumbnail."
            )
        )
        image_url = await U.wait_for_image(interaction, prompt)
        if image_url is None:
            return
        
        self.thumbnail = image_url
    
################################################################################
