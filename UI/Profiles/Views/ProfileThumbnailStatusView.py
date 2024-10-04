from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import ProfileImages
################################################################################

__all__ = ("ProfileThumbnailStatusView",)

################################################################################
class ProfileThumbnailStatusView(FroggeView):

    def __init__(self, owner: User, images: ProfileImages):
        
        super().__init__(owner, images)
        
        button_list = [
            SetThumbnailButton(),
            RemoveThumbnailButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class SetThumbnailButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Set Thumbnail Image",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_thumbnail(interaction)
        self.view.set_button_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.thumbnail_status(), view=self.view
        )
        
################################################################################
class RemoveThumbnailButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Thumbnail Image",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.disabled = self.view.ctx.thumbnail is None
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_thumbnail(interaction)
        self.view.set_button_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.thumbnail_status(), view=self.view
        )
        
################################################################################
