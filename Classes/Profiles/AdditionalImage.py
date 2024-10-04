from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar, Any, Dict
from discord import EmbedField, Embed
from discord.ext.pages import Page

from UI.Profiles import AdditionalImageEditView
from UI.Common import ConfirmCancelView, BasicTextModal
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import ProfileImages, FroggeBot
################################################################################

__all__ = ("AdditionalImage", )

AI = TypeVar("AI", bound="AdditionalImage")

################################################################################
class AdditionalImage:

    __slots__ = (
        "_parent",
        "_id",
        "_url",
        "_caption",
    )
    
################################################################################
    def __init__(
        self, 
        parent: ProfileImages, 
        _id: str,
        url: Optional[str] = None,
        caption: Optional[str] = None
    ) -> None:

        self._id: str = _id
        self._parent: ProfileImages = parent
        
        self._url: str = url
        self._caption: Optional[str] = caption
    
################################################################################
    @classmethod
    def new(cls: Type[AI], parent: ProfileImages, url: str) -> AI:
        
        new_id = parent.bot.api.create_additional_image(parent.profile_id, url)
        return cls(parent, new_id, url)
    
################################################################################
    @classmethod
    def load(cls: Type[AI], parent: ProfileImages, data: Dict[str, Any]) -> AI:
        
        return cls(
            parent=parent,
            _id=data["id"],
            url=data["image_url"],
            caption=data["caption"]
        )
    
################################################################################
    @property
    def bot(self) -> FroggeBot:
        
        return self._parent.bot
    
################################################################################
    @property
    def id(self) -> str:
        
        return self._id
    
################################################################################
    @property
    def url(self) -> str:
        
        return self._url
    
################################################################################
    @property
    def caption(self) -> Optional[str]:
        
        return self._caption
    
    @caption.setter
    def caption(self, value: Optional[str]) -> None:
        
        self._caption = value
        self.update()
        
################################################################################
    def update(self) -> None:
        
        self.bot.api.update_additional_image(self)
        
################################################################################
    def to_dict(self) -> dict:
        
        return {
            "url": self.url,
            "caption": self.caption
        }
    
################################################################################
    def delete(self) -> None:
        
        self.bot.api.delete_additional_image(self)
        self._parent.additional.remove(self)
        
################################################################################
    def compile(self) -> str:

        if self.caption is None:
            return self.url

        return f"[{self.caption}]({self.url})"

################################################################################
    def status(self) -> Embed:
        
        return U.make_embed(
            title="__Additional Image Info__",
            description="(This image can be see below.)",
            fields=[
                EmbedField(
                    name="__Permalink__",
                    value=self.url,
                    inline=False
                ),
                EmbedField(
                    name="__Caption__",
                    value=self.caption if self.caption is not None else "`Not Set`",
                    inline=False
                )
            ],
            image_url=self.url
        )
    
################################################################################
    def page(self) -> Page:
        
        return Page(embeds=[self.status()], custom_view=AdditionalImageEditView(self))
    
################################################################################
    async def set_caption(self, interaction) -> None:
        
        modal = BasicTextModal(
            title="Set Additional Image Caption",
            attribute="Caption",
            cur_val=self.caption,
            example="eg. 'My cat, Fluffy'",
            max_length=50,
            required=False
        )
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        self.caption = modal.value
    
################################################################################
    async def remove(self, interaction) -> None:
        
        prompt = U.make_embed(
            title="__Remove Additional Image__",
            description=(
                "Are you sure you want to remove this image from your profile? "
                "This action cannot be undone."
            )
        )
        view = ConfirmCancelView(interaction.user)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.delete()
    
################################################################################
    